import pyrealsense2 as rs
import numpy as np

from datetime import datetime

class Depthcamera():
    def __init__(self):
        # ---------------------------------------------------------
        # real sense
        # ---------------------------------------------------------
        # # ストリーム(Depth/Color)の設定
        print("start Depth camera")
        width : int= 640
        height : int= 480
        config = rs.config()
        config.enable_stream(rs.stream.color, width,height, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, width,height, rs.format.z16, 30)

        # RGB画像の生成
        self.colorizer = rs.colorizer()
        

        #フィルタ―の導入と設定
        #参照：https://qiita.com/keoitate/items/efe4212b0074e10378ec
        # decimarion_filterのパラメータ 複雑さを軽減する効果
        self.decimate = rs.decimation_filter()
        self.decimate.set_option(rs.option.filter_magnitude, 1)
        # spatial_filterのパラメータ 平滑化する効果
        self.spatial = rs.spatial_filter()
        self.spatial.set_option(rs.option.filter_magnitude, 1)
        self.spatial.set_option(rs.option.filter_smooth_alpha, 0.25)
        self.spatial.set_option(rs.option.filter_smooth_delta, 50)
        # hole_filling_filterのパラメータ 欠損データを補完する効果
        self.hole_filling = rs.hole_filling_filter()
        # disparity 視差に関する補正
        self.depth_to_disparity = rs.disparity_transform(True)
        self.disparity_to_depth = rs.disparity_transform(False)
        #temporal filter 時間方向の平滑化補正
        self.temporal = rs.temporal_filter()

        # ストリーミング開始
        self.pipeline = rs.pipeline()
        profile = self.pipeline.start(config)

        # Skip 5 first frames to give the Auto-Exposure time to adjust
        for x in range(5):
            self.pipeline.wait_for_frames()

        #get device information（デプスカメラの情報を取得）
        depth_sensor = profile.get_device().first_depth_sensor(); #print("depth sensor:",depth_sensor)
        self.depth_scale = depth_sensor.get_depth_scale(); #print("depth scale:",depth_scale)
        clipping_distance_in_meters = 1.0 # meter
        clipping_distance = clipping_distance_in_meters / self.depth_scale; print("clipping_distance:",clipping_distance)


        # Alignオブジェクト生成（異なる画角の対応のための補正）
        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.frameNo = 0
        self.timenow = ""

    def getFrames(self):
        
        # フレーム待ち(Color & Depth)
        frames = self.pipeline.wait_for_frames()
        self.frameNo = frames.get_frame_number()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        #画像の取得
        self.color_image = np.asanyarray(color_frame.get_data()) #RGB画像
        self.depth_image = np.asanyarray(self.colorizer.colorize(depth_frame).get_data()) #デプス情報のカラー化（深度画像の生成）
        
        #フィルターをかけていく。順番が大事。
        #20230108追加
        #参照：https://qiita.com/idev_jp/items/3eba792279d836646664
        depth_frame=self.decimate.process(depth_frame)
        depth_frame=self.depth_to_disparity.process(depth_frame)
        depth_frame=self.spatial.process(depth_frame)
        depth_frame=self.temporal.process(depth_frame)
        depth_frame=self.disparity_to_depth.process(depth_frame)
        depth_frame=self.hole_filling.process(depth_frame)

        #フィルターをかけた後に、深度画像とＲＧＢ画像を生成
        self.processed_depth_values = np.asanyarray(depth_frame.get_data()) #get values [mm]
        self.processed_depth_image = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())

    ## ---------------
    #    Return numpy arrays（生とフィルタ―後の深度情報とＲＧＢ画像を返すメソッド）
    ## ---------------
    def getColorImage(self):
        #print("called getColorimage()")
        return self.color_image

    def getDepthImage(self):  ##aligned
        #print("called getDepthimage()")
        return self.depth_image

    def getProcessedValues(self):
        #print("called getColorimage()")
        return self.processed_depth_values

    def getProcessedImage(self):
        #print("called getColorimage()")
        return self.processed_depth_image

    ## ---------------
    #    Return Frame Number（フレーム情報を返すメソッド）
    ## ---------------
    def getFrameNo(self):
        return self.frameNo

    def getDepthScale(self):
        return self.depth_scale

    def stop(self):
        self.pipeline.stop()

    def getTimenow(self):
        self.timenow :str = datetime.now().strftime( "%Y-%d-%m-%H-%M-%S.%f" ) 
        #print("in Depthcamera:",self.timenow)
        return self.timenow
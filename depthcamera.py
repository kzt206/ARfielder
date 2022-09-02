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

        #
        self.colorizer = rs.colorizer()
        
        #temporal filter
        self.temporal = rs.temporal_filter()

        #hole filling filter
        self.hole_filling = rs.hole_filling_filter()

        # ストリーミング開始
        self.pipeline = rs.pipeline()
        profile = self.pipeline.start(config)

        # Skip 5 first frames to give the Auto-Exposure time to adjust
        for x in range(5):
            self.pipeline.wait_for_frames()

        #get device information
        depth_sensor = profile.get_device().first_depth_sensor(); #print("depth sensor:",depth_sensor)
        self.depth_scale = depth_sensor.get_depth_scale(); #print("depth scale:",depth_scale)
        clipping_distance_in_meters = 1.0 # meter
        clipping_distance = clipping_distance_in_meters / self.depth_scale; print("clipping_distance:",clipping_distance)


        # Alignオブジェクト生成
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
        
        # if not depth_frame or not color_frame:
        #     continue

        self.color_image = np.asanyarray(color_frame.get_data())
        self.depth_image = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())
        #hole filter
        filled_depth_frame = self.hole_filling.process(depth_frame)
        self.filled_depth_values = np.asanyarray(filled_depth_frame.get_data()) #get values [mm]
        # print(filled_depth_values[100,100])
        self.filled_depth_image = np.asanyarray(self.colorizer.colorize(filled_depth_frame).get_data())

        #--------------
        #temporal filter and hole filter
        frames = []
        filteringFramesNo = 12
        for x in range(filteringFramesNo):
            frameset = self.pipeline.wait_for_frames()
            aligned_frameset = self.align.process(frameset)
            frames.append(aligned_frameset.get_depth_frame())
        for x in range(filteringFramesNo):
            temp_filtered = self.temporal.process(frames[x])
            temp_filtered = self.hole_filling.process(temp_filtered)
        self.temporal_filter_values = np.asanyarray(temp_filtered.get_data()) #get values [mm]
        self.temporal_filter_image = np.asanyarray(self.colorizer.colorize(temp_filtered).get_data())
        #-------------------
    ## ---------------
    #    Return numpy arrays
    ## ---------------
    def getColorImage(self):
        #print("called getColorimage()")
        return self.color_image

    def getDepthImage(self):  ##aligned
        #print("called getDepthimage()")
        return self.depth_image

    def getHoleFilledImage(self):
        #print("called getHoleFilledimage()")
        return self.filled_depth_image

    def getHoleFilledValues(self):
        #print("called getHoleFilledValues()")
        return self.filled_depth_values

    def getTemporalFilterImage(self):
        #print("called getHoleFilledValues()")
        return self.temporal_filter_image

    def getTemporalFilterValues(self):
        #print("called getHoleFilledValues()")
        return self.temporal_filter_values

    ## ---------------
    #    Return Frame Number
    ## ---------------
    def getFrameNo(self):
        return self.frameNo

    def getDepthScale(self):
        return self.depth_scale

    def stop(self):
        self.pipeline.stop()

    def getTimenow(self):
        self.timenow :str = datetime.now().strftime( "%Y-%m-%d-%H-%M-%S.%f" ) 
        #print("in Depthcamera:",self.timenow)
        return self.timenow
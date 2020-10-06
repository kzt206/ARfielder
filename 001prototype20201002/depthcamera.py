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

        # ストリーミング開始
        self.pipeline = rs.pipeline()
        profile = self.pipeline.start(config)

        # Alignオブジェクト生成
        align_to = rs.stream.color
        self.align = rs.align(align_to)

        # # フレーム待ち(Color & Depth)
        # frames = pipeline.wait_for_frames()
        # #frameNo = frames.get_frame_number()
        # aligned_frames = align.process(frames)
        # color_frame = aligned_frames.get_color_frame()
        # depth_frame = aligned_frames.get_depth_frame()
        
        # self.color_image = np.asanyarray(color_frame.get_data())
        # self.depth_image = np.asanyarray(colorizer.colorize(depth_frame).get_data())
        # #hole filter
        # hole_filling = rs.hole_filling_filter()
        # filled_depth_frame = hole_filling.process(depth_frame)
        # self.filled_depth_values = np.asanyarray(filled_depth_frame.get_data()) #get values [cm]
        # # print(filled_depth_values[100,100])
        # self.filled_depth_image = np.asanyarray(colorizer.colorize(filled_depth_frame).get_data())

        self.timenow = ""

    def getFrames(self):
        # フレーム待ち(Color & Depth)
        frames = self.pipeline.wait_for_frames()
        #frameNo = frames.get_frame_number()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()
        
        self.color_image = np.asanyarray(color_frame.get_data())
        self.depth_image = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())
        #hole filter
        hole_filling = rs.hole_filling_filter()
        filled_depth_frame = hole_filling.process(depth_frame)
        self.filled_depth_values = np.asanyarray(filled_depth_frame.get_data()) #get values [cm]
        # print(filled_depth_values[100,100])
        self.filled_depth_image = np.asanyarray(self.colorizer.colorize(filled_depth_frame).get_data())

    def getColorimage(self):
        #print("called getColorimage()")
        return self.color_image

    def getDepthimage(self):
        #print("called getDepthimage()")
        return self.depth_image

    def getHoleFilledimage(self):
        #print("called getHoleFilledimage()")
        return self.filled_depth_image

    def getHoleFilledValues(self):
        self.getFrames()
        #print("called getHoleFilledValues()")
        return self.filled_depth_values

    def getTimenow(self):
        self.timenow :str = datetime.now().strftime( "%Y-%d-%m-%H-%M-%S.%f" ) 
        #print("in Depthcamera:",self.timenow)
        return self.timenow

import pyrealsense2 as rs
import numpy as np
import time
import cv2

def initialize_camera():
    p = rs.pipeline()
    conf = rs.config()
    CAM_WIDTH, CAM_HEIGHT, CAM_FPS = 848,480,15
    conf.enable_stream(rs.stream.depth, CAM_WIDTH, CAM_HEIGHT, rs.format.z16, CAM_FPS)
    conf.enable_stream(rs.stream.color, CAM_WIDTH, CAM_HEIGHT, rs.format.rgb8, CAM_FPS)
    conf.enable_stream(rs.stream.infrared, CAM_WIDTH, CAM_HEIGHT, rs.format.y8, CAM_FPS)
    conf.enable_stream(rs.stream.accel,rs.format.motion_xyz32f,250)
    conf.enable_stream(rs.stream.gyro,rs.format.motion_xyz32f,200)
    # conf.enable_stream(rs.stream.accel)
    # conf.enable_stream(rs.stream.gyro,rs.format.motion_xyz32f,200)
    prof = p.start(conf)
    return p

def gyro_data(gyro):
    return np.asarray([gyro.x, gyro.y, gyro.z])


def accel_data(accel):
    return np.asarray([accel.x, accel.y, accel.z])


def main():
    # t0 = time.time()
    pipeline = initialize_camera()
    # print (time.time() - t0, "seconds elapsed")

    try:
        while True:

            frames = pipeline.wait_for_frames()
            frameNo = frames.get_frame_number()
            
            if frameNo % 10 != 0:
                continue

            for frame in frames:
                if frame.is_motion_frame():
                    accel = accel_data(frame.as_motion_frame().get_motion_data())
                    gyro = gyro_data(frame.as_motion_frame().get_motion_data())
                if frame.is_depth_frame():
                    depth_frame = frames.get_depth_frame()
                    color_frame = frames.get_color_frame()
                    infrared_frame = frames.get_infrared_frame()
            
            print()
            print("frame number: ",frameNo)
            print("accelerometer: ", accel)
            print("gyro: ", gyro)

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            infrared_image = np.asanyarray(infrared_frame.get_data())

            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            images = np.hstack((color_image, depth_colormap))

            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', images)

            cv2.namedWindow('Infrared', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Infrared', infrared_image)

            if cv2.waitKey(1) & 0xff == 27:  #27 = ESC
                break

    finally:
        pipeline.stop()

if __name__ == "__main__":
    main()
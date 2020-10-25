#https://github.com/IntelRealSense/librealsense/blob/jupyter/notebooks/depth_filters.ipynb

import numpy as np                        # fundamental package for scientific computing
import matplotlib.pyplot as plt           # 2D plotting library producing publication quality figures
import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API
print("Environment Ready")

# Setup:
pipe = rs.pipeline()
cfg = rs.config()
# cfg.enable_device_from_file("stairs.bag")
width : int= 640
height : int= 480
cfg.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
cfg.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
profile = pipe.start(cfg);print("pipline start")

# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):
    pipe.wait_for_frames()

#get device information
depth_sensor = profile.get_device().first_depth_sensor(); #print("depth sensor:",depth_sensor)
depth_scale = depth_sensor.get_depth_scale(); #print("depth scale:",depth_scale)
clipping_distance_in_meters = 1.0 # meter
clipping_distance = clipping_distance_in_meters / depth_scale
print("clipping_distance:",clipping_distance)

# Alignオブジェクト生成
align_to = rs.stream.color
align = rs.align(align_to)

# set frame Number
frameNo = 0

# Store next frameset for later processing:
frameset = pipe.wait_for_frames()
frameNo = frameset.get_frame_number()
aligned_frames = align.process(frameset)
color_frame = aligned_frames.get_color_frame()
depth_frame = aligned_frames.get_depth_frame()  #depth_frame = frameset.get_depth_frame()

# Cleanup:
# pipe.stop()
print("Color and depth Frames Captured")

# get frames for average filter  original
# profile = pipe.start(cfg)

frames = []
frameNos = []
hole_filling = rs.hole_filling_filter()
filteringNo = 10

for x in range(filteringNo):
    frameset = pipe.wait_for_frames()
    aligned_frameset = align.process(frameset)
    frameNos.append(frameset.get_frame_number())
    tmp_depth_frame = aligned_frames.get_depth_frame()
    frames.append(hole_filling.process(tmp_depth_frame))

pipe.stop();print("pipeline stopped")
print("Frames for average filter are Captured")

print("frameNo: ",frameNo)
print("frameNos: ",frameNos)



#visualising the Data
colorizer = rs.colorizer()
# first no filter depth frame
colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
fig1 = plt.figure()
ax1 = fig1.add_subplot()
ax1.set_title("aligned depth frame, Frame No: " + str(frameNo))
# ax1.set_rcParams["axes.grid"] = False
# ax1.set_rcParams['figure.figsize'] = [8, 4]
ax1.imshow(colorized_depth)

# hole filtered dapth frames
colorized_depth2 = np.asanyarray(colorizer.colorize(frames[0]).get_data())
fig2 = plt.figure()
ax2 = fig2.add_subplot()
ax2.set_title("hole filtered depth 0, Frame No: " + str(frameNos[0]))
# ax1.set_rcParams["axes.grid"] = False
# ax1.set_rcParams['figure.figsize'] = [8, 4]
ax2.imshow(colorized_depth2)

plt.show()
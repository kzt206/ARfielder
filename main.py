#############################################
##      D455 Depth画像の表示
#############################################
import pyrealsense2 as rs
import numpy as np
import cv2

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import time

import depthcamera


stepFrame = 0
stepConfigChage = 0
targetPointHorizontal =0
targetPointVertical = 0
frameCenterHorizontal= 0
frameCenterVertical= 0
frameHeight= 0
frameWidth= 0

figsizeWidth = 6
figsizeHeight = 6

colorMapType = 0

figureContour = plt.figure(figsize=(figsizeWidth,figsizeHeight))

#Configuration Update
def configLoad():
    global stepFrame,stepConfigChage
    global targetPointHorizontal,targetPointVertical
    global frameCenterHorizontal,frameCenterVertical,frameHeight,frameWidth
    global contourNear,contourFar
    global figsizeWidth,figsizeHeight
    global colorMapType

    configDic = {}
    with open('config.txt', 'r') as configFile:
        for line in configFile:
            elements = line.split(',') 
            configDic[elements[0]] = int(elements[1])
    print(configDic)

    stepFrame = configDic['stepFrame']
    stepConfigChage = configDic['stepConfigChage']
    targetPointHorizontal = configDic['targetPointHorizontal']
    targetPointVertical = configDic['targetPointVertical']
    targetPointVertical = configDic['targetPointVertical']
    frameCenterHorizontal= configDic['frameCenterHorizontal']
    frameCenterVertical= configDic['frameCenterVertical']
    frameHeight= configDic['frameHeight']
    frameWidth= configDic['frameWidth']
    contourNear = configDic['contourNear']
    contourFar = configDic['contourFar']
    figsizeWidth = configDic['figsizeWidth']
    figsizeHeight = configDic['figsizeHeight']
    colorMapType = configDic['colorMapType']

def main():
    dCamera = depthcamera.Depthcamera()

    #initial configuration load
    global stepFrame,stepConfigChage
    global targetPointHorizontal,targetPointVertical
    global frameCenterHorizontal,frameCenterVertical,frameHeight,frameWidth
    global figsizeWidth,figsizeHeight
    global colorMapType
    configLoad()

    colormaps = ('jet_r','jet','prism','summer','terrain','terrain_r','ocean','ocean_r','gist_earth','gist_earth_r','rainbow','rainbow_r')

    #Begin Rendering
    try:
        while True:

            #time.sleep(1000)
            dCamera.getFrames()
            frameNo = dCamera.getFrameNo()

            if frameNo % stepFrame != 0:
                continue

            #Configuration Update
            if frameNo % stepConfigChage == 0:
                configLoad()

            #print(frameNo)

            #------
            # get image from depth camera
            #------
            color_image = dCamera.getColorImage()
            depth_image = dCamera.getDepthImage()   #aligned
            hole_filled_image = dCamera.getHoleFilledImage()
            filled_depth_values = dCamera.getHoleFilledValues() 

            # Depth画像前処理(1m以内を画像化)  
            # clipping_distance = 1000 # [cm]
            # grey_color = 153
            # depth_image_3d = np.dstack((fille_depth_values,fille_depth_values,fille_depth_values))
            # bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
            
            #-----
            #put Target point distance 
            #-----
            # targetPointHorizontal = 320
            # targetPointVertical = 240
            #put Text Time and depth
            textTime=dCamera.getTimenow()
            textDepth="depth:" +str(filled_depth_values[targetPointVertical,targetPointHorizontal])+"[mm]"
            pointTime=(30,30)
            pointDepth=(targetPointHorizontal+10,targetPointVertical+5)
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 0, 255) # Blue, Green, Red
            thickness = 2
            line_type = cv2.LINE_8
            cv2.putText(color_image, textTime, pointTime, font_face, font_scale, color, thickness, line_type)
            cv2.putText(color_image, textDepth, pointDepth, font_face, font_scale, color, thickness, line_type)
            cv2.rectangle(color_image, (targetPointHorizontal-2,targetPointVertical-2), (targetPointHorizontal+2,targetPointVertical+2), color, thickness=-1)

            #put Text of Step Frame
            textFrame="StepFrame:" + str(stepFrame)
            pointTextFrame=(30,60)
            cv2.putText(color_image, textFrame, pointTextFrame, font_face, font_scale, color, thickness, line_type)

            #put Frame 1
            # frameCenterHorizontal = 320
            # frameCenterVertical = 240
            # frameHeight = 120
            # frameWidth = 120
            frameT = int(frameCenterVertical-frameHeight/2)
            frameB = int(frameCenterVertical+frameHeight/2)
            frameL = int(frameCenterHorizontal-frameWidth/2)
            frameR = int(frameCenterHorizontal+frameWidth/2)
            cv2.rectangle(color_image, (frameL,frameT), (frameR,frameB), color, thickness=1)

            #---------------------
            # contour
            #---------------------
            plt.clf()
            figureContour.set_figheight(figsizeHeight)
            figureContour.set_figwidth(figsizeWidth)
            axContour = figureContour.add_subplot()
            # near=600
            # far =1200
            axContour.set_title("Display Depth:"+str(contourNear)+" - "+str(contourFar)+" [cm]\n"+"cmap:"+colormaps[colorMapType])
            levelmapColor = np.linspace(contourNear,contourFar,20)
            bounds=np.linspace(contourNear,contourFar,20)
            levelmapContour = np.linspace(contourNear,contourFar,10)
            #axContour.text(200,200,textTime)
            axContour.set_xlim([frameL,frameR])
            axContour.set_ylim([frameB,frameT])
            #print(colormaps[colorMapType],colorMapType)
            
            ### colormap test ###
            top = cm.get_cmap('Oranges_r', 128)
            bottom = cm.get_cmap('Blues', 128)
            newcolors = np.vstack((top(np.linspace(0, 1, 128)),
                       bottom(np.linspace(0, 1, 128))))
            newcmp = ListedColormap(newcolors, name='OrangeBlue')
            #cont1 = axContour.contourf(filled_depth_values,cmap=newcmp,levels=levelmapColor) #Color,levels=[0.75,0.8,0.85,0.9,0.95,1.,1.05]
            ###########

            cont1 = axContour.contourf(filled_depth_values,cmap=colormaps[colorMapType],levels=levelmapColor) #Color,levels=[0.75,0.8,0.85,0.9,0.95,1.,1.05]
            cbar = figureContour.colorbar(cont1,orientation="vertical",format="%3.2f") # カラーバーの表示
            axContour.contour(filled_depth_values,levels=levelmapContour)
            cbar.set_label('depth [mm]',size=12)
            # axContour.set_aspect(frameHeight/frameWidth)
            axContour.set_aspect('equal')
            plt.savefig("tempFigure.png")
            coutour_image = cv2.imread("tempFigure.png")

            #----
            # レンダリング
            #----
            # cv2.WINDOW_AUTOSIZE：デフォルト。ウィンドウ固定表示
            # cv2.WINDOW_NORMAL：ウィンドウのサイズを変更可能にする
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            images = np.hstack((color_image, depth_image))
            cv2.namedWindow('Align', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align', images)

            # images2 = np.hstack((color_image, hole_filled_image))
            # cv2.namedWindow('Hole filled', cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('Hole filled', images2)

            # images3 = np.hstack((contour_image))
            cv2.namedWindow('Contour', cv2.WINDOW_NORMAL)
            cv2.imshow('Contour', coutour_image)

            # blended
            images4 = cv2.addWeighted(src1=color_image,alpha=0.5,src2=hole_filled_image,beta=0.5,gamma=0)
            cv2.namedWindow('Blended Image', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Blended Image', images4)

            #time.sleep(1000)
            #print(dCamera.getFrameNo())

            if cv2.waitKey(1) & 0xff == 27:  #27 = ESC
                break

    finally:
        # ストリーミング停止
        dCamera.stop()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    main()
#############################################
##      D455 Depth画像の表示
#############################################
import pyrealsense2 as rs
import numpy as np
import cv2

#グラフ描画のためのライブラリ
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

#プロット領域をピクセル単位で指定するためのライブラリ
from mpl_toolkits.axes_grid1 import Divider, Size # 追加
from mpl_toolkits.axes_grid1.mpl_axes import Axes # 追加

import time

import depthcamera #独自のデプスカメラ用のライブラリ

##
#初期設定（後ほど、設定ファイルを読み込むことで変更される）
##
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

#matplotlibの描画画面の宣言。これが、プロジェクトに投影される。
# figureContour = plt.figure(figsize=(figsizeWidth,figsizeHeight))
ax_w_px = 630  # プロット領域の幅をピクセル単位で指定   箱の幅630mm
ax_h_px = 480  # プロット領域の高さをピクセル単位で指定 箱の高さ480mm


###########################################################
# サイズ指定のための処理 ↓↓ ここから ↓↓ 
fig_dpi = 100
ax_w_inch = ax_w_px / fig_dpi
ax_h_inch = ax_h_px / fig_dpi
ax_margin_inch = (0.5, 0.5, 0.5, 0.5)  # Left,Top,Right,Bottom [inch]

fig_w_inch = ax_w_inch + ax_margin_inch[0] + ax_margin_inch[2] 
fig_h_inch = ax_h_inch + ax_margin_inch[1] + ax_margin_inch[3]

figureContour = plt.figure( dpi=fig_dpi, figsize=(fig_w_inch, fig_h_inch))
ax_p_w = [Size.Fixed(ax_margin_inch[0]),Size.Fixed(ax_w_inch)]
ax_p_h = [Size.Fixed(ax_margin_inch[1]),Size.Fixed(ax_h_inch)]
divider = Divider(figureContour, (0.0, 0.0, 1.0, 1.0), ax_p_w, ax_p_h, aspect=False)
ax = Axes(figureContour, divider.get_position())
ax.set_axes_locator(divider.new_locator(nx=1,ny=1))
figureContour.add_axes(ax)
# サイズ指定のための処理 ↑↑ ここまで ↑↑
###########################################################

#Configuration Update
#設定リストを読み込むメソッド
def configLoad():
    # global変数の宣言
    global stepFrame,stepConfigChage
    global targetPointHorizontal,targetPointVertical
    global frameCenterHorizontal,frameCenterVertical,frameHeight,frameWidth
    global contourNear,contourFar
    global figsizeWidth,figsizeHeight
    global colorMapType

    # 設定ファイルの中で、整数かどうかを判別するための辞書型リスト
    isIntDic={'stepFrame':True,'stepConfigChage':True,'targetPointHorizontal':True,'targetPointVertical':True,
                'frameCenterHorizontal':True,'frameCenterVertical':True,'frameHeight':True,'frameWidth':True,
                'contourNear':True,'contourFar':True,'figsizeWidth':True,'figsizeHeight':True,'colorMapType':True,
                'isPause':True,'f':False,'num':True}

    # ファイルを開いて読み込んで、辞書型リストにインプットする
    configDic = {}
    with open('config.txt', 'r') as configFile:
        for line in configFile:
            elements = line.split(',') 
            if(isIntDic[elements[0]]): #整数かどうか判別
                configDic[elements[0]] = int(elements[1].replace("\n", "")) #整数型の変数の読み込み。「改行記号」を除去
            else:
                configDic[elements[0]] = float(elements[1].replace("\n", "")) #実数型の変数の読み込み。「改行記号」を除去
    print(configDic)

    #読み込んだ設定を辞書型リストからglobal変数に代入
    stepFrame = configDic['stepFrame'] #ステップのスキップ設定
    stepConfigChage = configDic['stepConfigChage'] #
    targetPointHorizontal = configDic['targetPointHorizontal'] #距離情報を取得するポイントの設定（横方向）
    targetPointVertical = configDic['targetPointVertical'] #距離情報を取得するポイントの設定（縦方向）
    frameCenterHorizontal= configDic['frameCenterHorizontal'] #プロジェクションに反映するフレームの中心位置の設定（横方向）
    frameCenterVertical= configDic['frameCenterVertical'] #プロジェクションに反映するフレームの中心位置の設定（縦方向）
    frameHeight= configDic['frameHeight'] #プロジェクションに反映するフレーム高さの設定
    frameWidth= configDic['frameWidth'] #プロジェクションに反映するフレーム幅の設定
    contourNear = configDic['contourNear'] #プロジェクション等高線等の手前側（高い方）距離の設定
    contourFar = configDic['contourFar'] #プロジェクション等高線等の奥側（低い方）距離の設定
    figsizeWidth = configDic['figsizeWidth'] #グラフの大きさ設定（横方向）　※非使用
    figsizeHeight = configDic['figsizeHeight'] #グラフの大きさ設定（縦方向）　※非使用
    colorMapType = configDic['colorMapType'] #高さ情報のカラーマップの設定

#メインとなるメソッド
def main():
    dCamera = depthcamera.Depthcamera() #デプスカメラを操作するインスタンスの宣言

    #initial configuration load
    global stepFrame,stepConfigChage
    global targetPointHorizontal,targetPointVertical
    global frameCenterHorizontal,frameCenterVertical,frameHeight,frameWidth
    global figsizeWidth,figsizeHeight
    global colorMapType
    configLoad()

    colormaps = ('jet_r','jet','prism','summer','terrain','terrain_r','ocean','ocean_r','gist_earth','gist_earth_r','rainbow','rainbow_r')

    #Begin Rendering
    #レンダリングをする
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

            #------
            # get image from depth camera
            #------
            color_image = dCamera.getColorImage()
            depth_image = dCamera.getDepthImage()   #aligned

            processed_image=dCamera.getProcessedImage()
            processed_values=dCamera.getProcessedValues()

            #-----
            #put Target point distance 
            #-----
            #put Text Time ,depth and the frame number
            textTime=dCamera.getTimenow()
            textDepth="depth:" +str(processed_values[targetPointVertical,targetPointHorizontal])+"[mm]"
            pointTime=(30,30)
            pointDepth=(targetPointHorizontal+10,targetPointVertical+5)
            textFrameNo = "Frame:" + str(frameNo)
            pointFrameNo=(30,90)  #Horizontal,Vertical
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 0, 255) # Blue, Green, Red
            colorDepth = (0, 255, 0) # Blue, Green, Red
            thickness = 2
            line_type = cv2.LINE_8
            cv2.putText(color_image, textTime, pointTime, font_face, font_scale, color, thickness, line_type)
            cv2.putText(color_image, textDepth, pointDepth, font_face, font_scale, colorDepth, thickness, line_type)
            cv2.rectangle(color_image, (targetPointHorizontal-2,targetPointVertical-2), (targetPointHorizontal+2,targetPointVertical+2), colorDepth, thickness=-1)
            cv2.putText(color_image, textFrameNo, pointFrameNo, font_face, font_scale, color, thickness, line_type)

            #put Text of Step Frame
            textFrame="StepFrame:" + str(stepFrame)
            pointTextFrame=(30,60)
            cv2.putText(color_image, textFrame, pointTextFrame, font_face, font_scale, color, thickness, line_type)

            #put Frame 1
            frameT = int(frameCenterVertical-frameHeight/2)
            frameB = int(frameCenterVertical+frameHeight/2)
            frameL = int(frameCenterHorizontal-frameWidth/2)
            frameR = int(frameCenterHorizontal+frameWidth/2)
            cv2.rectangle(color_image, (frameL,frameT), (frameR,frameB), color, thickness=2)

            #put Grid
            width = 640
            height = 480
            colorGrid = (120, 120, 120) # Blue, Green, Red
            for i in range(0,width,50):
                cv2.line(color_image,(0,i),(width,i),colorGrid)
            for i in range(0,height,50):
                cv2.line(color_image,(i,0),(i,height),colorGrid)

            #---------------------
            # contour
            #---------------------
            plt.clf()

            # サイズ指定のための処理 ↓↓ ここから ↓↓ 
            ax_p_w = [Size.Fixed(ax_margin_inch[0]),Size.Fixed(ax_w_inch)]
            ax_p_h = [Size.Fixed(ax_margin_inch[1]),Size.Fixed(ax_h_inch)]
            divider = Divider(figureContour, (0.0, 0.0, 1.0, 1.0), ax_p_w, ax_p_h, aspect=False)
            axContour = Axes(figureContour, divider.get_position())
            axContour.set_axes_locator(divider.new_locator(nx=1,ny=1))
            figureContour.add_axes(axContour)
            # サイズ指定のための処理 ↑↑ ここまで ↑↑

            # near=600
            # far =1200
            axContour.set_title("Display Depth:"+str(contourNear)+" - "+str(contourFar)+" [cm]\n"+"cmap:"+colormaps[colorMapType])
            contourArray1 = np.arange(contourNear-40,contourNear,5)  # pitch mm
            contourArray2 = np.arange(contourNear,contourFar,5)  #pitch mm
            contourArray3 = np.arange(contourFar,contourFar+40,5) #pitch mm
            levelmapColor=np.append(contourArray1,contourArray2)
            levelmapColor=np.append(levelmapColor,contourArray3) 
            # print(levelmapColor[:])
            levelmapContour = levelmapColor
            axContour.set_xlim([frameL,frameR])
            axContour.set_ylim([frameB,frameT])
            
            ### colormap test ###
            top = cm.get_cmap('Oranges_r', 128)
            bottom = cm.get_cmap('Blues', 128)
            newcolors = np.vstack((top(np.linspace(0, 1, 128)),
                       bottom(np.linspace(0, 1, 128))))
            newcmp = ListedColormap(newcolors, name='OrangeBlue')
            ###########

            cont1 = axContour.contourf(processed_values,cmap=colormaps[colorMapType],levels=levelmapColor,extend="both") #Color,levels=[0.75,0.8,0.85,0.9,0.95,1.,1.05]
            cont1.cmap.set_under('pink')
            # cbar = figureContour.colorbar(cont1,orientation="vertical",format="%3.2f") # カラーバーの表示
            axContour.contour(processed_values,levels=levelmapContour)
            # axContour.contour(filled_depth_values,levels=levelmapContour)
            # cbar.set_label('depth [mm]',size=12)
            # axContour.set_aspect('equal')
            plt.savefig("tempFigure.png")
            contour_image = cv2.imread("tempFigure.png",1)

            #----
            # レンダリング
            #----
            # cv2.WINDOW_AUTOSIZE：デフォルト。ウィンドウ固定表示
            # cv2.WINDOW_NORMAL：ウィンドウのサイズを変更可能にする
            # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            cv2.namedWindow('MainImages', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('MainImages', color_image)

            #コンター画像をopencvで表示。
            #アスペクト比を保つために
            #https://gist.github.com/kefir-/03cea3e3b17b7a74a7cdcf57a2159a79
            cv2.namedWindow('forARsunaba_Contour', cv2.WINDOW_NORMAL)
            ci_height, ci_width = contour_image.shape[:2]
            cv2.resizeWindow('forARsunaba_Contour', ci_width, ci_height)
            cv2.imshow('forARsunaba_Contour', contour_image)

            # blended
            images4 = cv2.addWeighted(src1=color_image,alpha=0.5,src2=processed_image,beta=0.5,gamma=0)
            cv2.namedWindow('Blended Image', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Blended Image', images4)

            #time.sleep(1000)

            if cv2.waitKey(1) & 0xff == 27:  #27 = ESC
                break

    finally:
        # ストリーミング停止
        dCamera.stop()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    main()
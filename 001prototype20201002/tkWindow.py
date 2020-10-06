import tkinter as tk
from tkinter import ttk
from tkinter import font

#import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
from datetime import datetime
import PIL.Image, PIL.ImageTk

import tkWidgets
import depthcamera

class Application(tk.Frame):
    
    color_image = np.zeros(1)
    depth_image = np.zeros(1)
    hole_filled_image = np.zeros(1)
    filled_depth_values = np.zeros(1)
    dcamera = depthcamera.Depthcamera()
    
    def __init__(self,master):
        super().__init__(master)

        self.master.geometry("1400x700")
        self.master.title("Root window")

        self.window = []
        self.user = []

        # ---------------------------------------------------------
        # real sense
        # ---------------------------------------------------------
        # self.dcamera = depthcamera.Depthcamera()
   
        # ---------------------------------------------------------
        # Graph figure
        # ---------------------------------------------------------
        #make graph https://qiita.com/kotai2003/items/45953b4d037a62b2042c
        self.x = np.arange(100)
        self.y = np.arange(100)
        self.figure1 = plt.figure()
        #self.ax1 = self.figure1.add_subplot()
        
        # ---------------------------------------------------------
        # Font
        # ---------------------------------------------------------
        self.font_frame = font.Font( family="Meiryo UI", size=15, weight="normal" )
        self.font_btn_big = font.Font( family="Meiryo UI", size=20, weight="bold" )
        self.font_btn_small = font.Font( family="Meiryo UI", size=12, weight="bold" )

        self.font_lbl_bigger = font.Font( family="Meiryo UI", size=45, weight="bold" )
        self.font_lbl_big = font.Font( family="Meiryo UI", size=30, weight="bold" )
        self.font_lbl_middle = font.Font( family="Meiryo UI", size=15, weight="bold" )
        self.font_lbl_small = font.Font( family="Meiryo UI", size=12, weight="normal" )

        # ---------------------------------------------------------
        # Widget
        # ---------------------------------------------------------

        tkWidgets.Widgets.create_widgets(self)

        # ---------------------------------------------------------
        # Canvas Update
        # ---------------------------------------------------------

        self.delay = 500 #[mili seconds]
        self.update()

    def update(self):

        # -------------------------
        #   left side
        # -------------------------
        self.filled_depth_values = self.dcamera.getHoleFilledValues()
        #
        if self.radioValue.get() == 1:
            main_image = self.dcamera.getHoleFilledimage()
        elif self.radioValue.get()== 2:
            main_image = self.dcamera.getDepthimage()
        else:
            main_image = self.dcamera.getColorimage()
        #
        self.color_image = self.dcamera.getColorimage()
        self.depth_image = self.dcamera.getDepthimage()
        self.hole_filled_image = self.dcamera.getHoleFilledimage()

        #Get a frame from the video source
        #print(filled_depth_values[240,320])
        #put text
        textTime=datetime.now().strftime( "%Y-%d-%m-%H-%M-%S.%f" ) 
        textDepth="depth:" +str(self.filled_depth_values[240,320])+"[cm]"
        pointTime=(50,100)
        pointDepth=(320+10,240+5)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 0, 255) # Blue, Green, Red
        thickness = 2
        line_type = cv2.LINE_8
        cv2.putText(main_image, textTime, pointTime, font_face, font_scale, color, thickness, line_type)
        cv2.putText(main_image, textDepth, pointDepth, font_face, font_scale, color, thickness, line_type)
        cv2.rectangle(main_image, (320-2,240-2), (320+2,240+2), color, thickness=-1)

        frameHeight = 120
        frameWidth = 120
        frameT = int(240-frameHeight/2)
        frameB = int(240+frameHeight/2)
        frameL = int(320-frameWidth/2)
        frameR = int(320+frameWidth/2)
        cv2.rectangle(main_image, (frameL,frameT), (frameR,frameB), color, thickness=1)

        frame = cv2.cvtColor(main_image, cv2.COLOR_BGR2RGB)
        #height_tmp=frame.shape[0]
        #width_tmp=frame.shape[1]
        #frame = cv2.resize(frame,(int(width_tmp*2),int(height_tmp*2)))
        #self.photo2 = PIL.Image.open(PIL.Image.fromarray(frame))
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        #print(self.photo.height())
        #self.photo -> Canvas
        self.canvas1.create_image(0,0, image= self.photo, anchor = tk.NW)


        # -------------------------
        #   right side
        # -------------------------
        #graph
        plt.clf()
        ax1 = self.figure1.add_subplot()
        near=600
        far =700
        ax1.set_title("Display Depth:"+str(near)+" - "+str(far)+" [cm]")
        levelmap = np.linspace(near,far,100)
        levelmap2 = np.linspace(near,far,15)
        ax1.set_xlim([0,100])
        ax1.set_ylim([0,100])
        ax1.text(10,10,textTime)
        cont1 = ax1.contourf(self.filled_depth_values,cmap='jet_r',levels=levelmap) #,levels=[0.75,0.8,0.85,0.9,0.95,1.,1.05]
        cbar = self.figure1.colorbar(cont1,orientation="vertical",format="%3.2f") # カラーバーの表示
        ax1.contour(self.filled_depth_values,levels=levelmap2)
        cbar.set_label('distance [cm]',size=12)
        ax1.set_xlim([frameL,frameR])
        ax1.set_ylim([frameB,frameT])
        ax1.set_aspect('equal', adjustable='box')
        #self.ax1.plot(self.x,self.y*self.radioValue.get())
        #self.ax1.text(10,10,text)
        self.canvas2.draw()
    
        #radio button
        #print(self.radioValue.get())

        ## ----------------------------- 
        # update
        ## ----------------------------

        #print("main window update finished")
        self.master.after(self.delay, self.update)

    def press_close_button(self):
        plt.clf()
        plt.close()
        self.master.destroy()
        #self.pipeline.stop()
        #self.vcap.release()

    def press_realwindow_button(self):
        self.window.append(tk.Toplevel())
        self.user.append(User(self.window[len(self.window)-1],len(self.window)))








class User(tk.Frame):
    def __init__(self,master,num):
        super().__init__(master)
        self.pack()
        self.num = num
        master.geometry("690x550")
        master.title(str(self.num)+"つ目に作成されたウィンドウ")

        print("new window created !")

        # ---------------------------------------------------------
        # Font
        # ---------------------------------------------------------
        self.font_frame = font.Font( family="Meiryo UI", size=15, weight="normal" )

        # ---------------------------------------------------------
        # Widget
        # ---------------------------------------------------------

        self.create_widgets()


        # ---------------------------------------------------------
        # Canvas Update
        # ---------------------------------------------------------

        self.delay = 500 #[mili seconds]
        self.update()

    def create_widgets(self):
        
        self.width = 640
        self.height = 480

        #Frame_Camera
        self.frame_cam = tk.LabelFrame(self.master, text = 'Camera', font=self.font_frame)
        self.frame_cam.place(x = 10, y = 10)
        self.frame_cam.configure(width = self.width+30, height = self.height+50)
        self.frame_cam.grid_propagate(0)

        #Canvas 1
        self.canvas1 = tk.Canvas(self.frame_cam)
        self.canvas1.configure( width= self.width, height=self.height)
        self.canvas1.grid(column= 0, row=0,padx = 10, pady=10)

    def update(self):
        self.filled_depth_values = Application.dcamera.getHoleFilledValues()
        #
        # if self.radioValue.get() == 1:
        #     main_image = self.dcamera.getHoleFilledimage()
        # elif self.radioValue.get()== 2:
        #     main_image = self.dcamera.getDepthimage()
        # else:
        main_image = Application.dcamera.getColorimage()
        #print(main_image.shape)
        #
        #Get a frame from the video source
        #put text
        textTime=datetime.now().strftime( "%Y-%d-%m-%H-%M-%S.%f" )
        textDepth="depth:" +str(self.filled_depth_values[240,320])+"[cm]"
        pointTime=(50,100)
        pointDepth=(320+10,240+5)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 0, 255) # Blue, Green, Red
        thickness = 2
        line_type = cv2.LINE_8
        cv2.putText(main_image, textTime, pointTime, font_face, font_scale, color, thickness, line_type)
        cv2.putText(main_image, textDepth, pointDepth, font_face, font_scale, color, thickness, line_type)
        cv2.rectangle(main_image, (320-2,240-2), (320+2,240+2), color, thickness=-1)

        #put frame
        frameHeight = 120
        frameWidth = 120
        frameT = int(240-frameHeight/2)
        frameB = int(240+frameHeight/2)
        frameL = int(320-frameWidth/2)
        frameR = int(320+frameWidth/2)
        cv2.rectangle(main_image, (frameL,frameT), (frameR,frameB), color, thickness=1)

        frame = cv2.cvtColor(main_image, cv2.COLOR_BGR2RGB)
        height_tmp=frame.shape[0]
        width_tmp=frame.shape[1]
        scale = 1
        frame = cv2.resize(frame,(int(width_tmp*scale),int(height_tmp*scale)))
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))

        #self.photo -> Canvas
        self.canvas1.create_image(0,0, image= self.photo, anchor = tk.NW)

        self.master.after(self.delay, self.update)

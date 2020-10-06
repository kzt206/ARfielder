import tkinter as tk
from tkinter import ttk
from tkinter import font

import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Widgets(tk.Frame):
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

        #Frame_Graph 
        self.frame_graph = tk.LabelFrame(self.master, text = 'Graph', font=self.font_frame)
        self.frame_graph.place(x = 700, y = 10)
        self.frame_graph.configure(width = self.width+30, height = self.height+50)
        self.frame_graph.grid_propagate(0)

        #Canvas 2 for graph
        self.canvas2 = FigureCanvasTkAgg(self.figure1, self.frame_graph)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Control frame
        self.frame_btn = tk.LabelFrame( self.master, text='Control', font=self.font_frame )
        self.frame_btn.place( x=10, y=550 )
        self.frame_btn.configure( width=1300, height=120 )
        self.frame_btn.grid_propagate( 0 )

        # Close
        self.btn_close = tk.Button( self.frame_btn, text='Close', font=self.font_btn_small )
        self.btn_close.configure( width=10, height=1, command=self.press_close_button )
        self.btn_close.grid( column=0, row=0, padx=20, pady=5 )

        # filter image
        self.btn_close = tk.Button( self.frame_btn, text='Open filter ', font=self.font_btn_small )
        self.btn_close.configure( width=15, height=1, command=self.press_realwindow_button )
        self.btn_close.grid( column=2, row=0, padx=10, pady=5 )

        # depth image
        self.btn_close = tk.Button( self.frame_btn, text='Open depth', font=self.font_btn_small )
        self.btn_close.configure( width=15, height=1, command=self.press_realwindow_button )
        self.btn_close.grid( column=3, row=0, padx=10, pady=5 )

        # real image
        self.btn_close = tk.Button( self.frame_btn, text='Open real', font=self.font_btn_small )
        self.btn_close.configure( width=15, height=1, command=self.press_realwindow_button )
        self.btn_close.grid( column=4, row=0, padx=10, pady=5 )

        # contour image
        self.btn_close = tk.Button( self.frame_btn, text='Open contour', font=self.font_btn_small )
        self.btn_close.configure( width=15, height=1, command=self.press_realwindow_button )
        self.btn_close.grid( column=5, row=0, padx=10, pady=5 )

        # filter label
        #label_filter = tk.Label(self.frame_btn,text='Hole filter',font=self.font_btn_small)
        #label_filter.grid(column=2,row=0)

        # Radio Button
        self.radioValue = tk.IntVar()
        self.radioValue.set(1)
        rb1 = tk.Radiobutton(self.frame_btn,text="FilterDepth",value=1,variable=self.radioValue,font=self.font_btn_small)
        rb2 = tk.Radiobutton(self.frame_btn,text="RawDepth",value=2,variable=self.radioValue,font=self.font_btn_small)
        rb3 = tk.Radiobutton(self.frame_btn,text="RealImage",value=3,variable=self.radioValue,font=self.font_btn_small)
        rb1.configure(width=10, height=1)
        rb2.configure(width=10, height=1)
        rb3.configure(width=10, height=1)
        rb1.grid(column=2,row=1,padx=10, pady=5)
        rb2.grid(column=3,row=1,padx=10, pady=5)
        rb3.grid(column=4,row=1,padx=10, pady=5)
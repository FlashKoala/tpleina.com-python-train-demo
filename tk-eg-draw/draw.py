# -*- coding:utf-8 -*-
#
#
##################################################
######## Please Don't Remove Author Name #########
############### Thanks ###########################
##################################################
#
#
__author__='''
######################################################
                www.tpleina.com                         
######################################################
    Flash Koala
    http://www.tpleina.com  
    雷那网 - 一个有温度的Python兴趣屋！
######################################################
'''

from collections import OrderedDict
import functools
import math
import tkinter as tk
from tkinter import ttk,colorchooser


def get_point_distance(p1, p2):
    """获得两个点的距离"""
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return math.sqrt(math.pow(x,2) + math.pow(y,2))


class Drawer(object):
    """画板实现类，功能：
    1. 绘制图像：直线、矩形、椭圆、多边形
    2. 支持铅笔工具使用
    3. 填充色、边线颜色、线条粗细等设置
    4. 橡皮擦功能
    5. 图像拖动等
    """
    def __init__(self, mw):
        self.mw = mw
        self.initWidgets()

    def initWidgets(self):
        # 初始化图标
        self.init_icons()
        # 初始参数
        self.x_pos, self.y_pos = -1, -1
        self.cur_x_pos, self.cur_y_pos = -1, -1
        # 选择绘制图像
        self.cur_drawing = 'juxing'
        # 中间临时cv对象
        self.temp_cv = None
        # 初始填充颜色
        self.fill_color = None
        # 初始边线颜色
        self.border_color = 'black'
        # 初始边线粗细值
        self.border = tk.IntVar()
        self.border.set(2)
        # 用于配置多边形配套熟悉
        self.pointer = []
        self.pointer_coordinate = []
        self.move_cvs = []
        # 调用init_toolbar初始化工具条
        self.init_toolbar()
        # 初始化主面板Frame容器
        self.init_mainboard()

    def init_mainboard(self):
        """初始绘画区"""
        self.mf = ttk.Frame(self.mw)
        self.mf.pack(fill=tk.BOTH, expand=True)
        self.cv = tk.Canvas(self.mf, background='white')
        self.cv.pack(fill=tk.BOTH, expand=True)
        # 右键按住移动事件
        self.cv.bind('<B1-Motion>', self.mouse_move)
        # 右键释放事件
        self.cv.bind('<ButtonRelease-1>', self.mouse_release)
        # 右键事件，用于绘制多边形
        self.cv.bind('<Button-1>', self.mouse_click)
        # 鼠标中间按住拖动，用于移动图形
        self.cv.bind('<B2-Motion>', self.mouse_mid)
        # 鼠标中间释放
        self.cv.bind('<ButtonRelease-2>', self.mouse_mid_release)

    def init_icons(self):
        """初始化图标"""
        self.mw.bold_icon = tk.PhotoImage(file='image/bold.png')
        self.mw.border_icon = tk.PhotoImage(file='image/border.png')
        self.mw.dbx_icon = tk.PhotoImage(file='image/dbx.png')
        self.mw.juxing_icon = tk.PhotoImage(file='image/juxing.png')
        self.mw.line_icon = tk.PhotoImage(file='image/line.png')
        self.mw.pencil_icon = tk.PhotoImage(file='image/pencil.png')
        self.mw.tianchong_icon = tk.PhotoImage(file='image/tianchong.png')
        self.mw.tuoyuan_icon = tk.PhotoImage(file='image/tuoyuan.png')
        self.mw.xiangpi_icon = tk.PhotoImage(file='image/xiangpi.png')
    
    def init_toolbar(self):
        """创建窗口工具栏菜单"""
        self.btns = {}
        toolframe = tk.Frame(self.mw, height=43, bg='white')
        toolframe.pack(fill=tk.X)
        icons = {'line': self.mw.line_icon, # 画线
                    'juxing': self.mw.juxing_icon, # 画矩形
                    'tuoyuan': self.mw.tuoyuan_icon, # 画椭圆
                    'dbx': self.mw.dbx_icon, # 画多边形
                    'pencil': self.mw.pencil_icon, # 铅笔工具
                    'border': self.mw.border_icon, # 边线颜色
                    'tianchong': self.mw.tianchong_icon, # 内容颜色
                    'bold': self.mw.bold_icon, # 边线粗细
                    'xiangpi': self.mw.xiangpi_icon # 橡皮擦工具
                    }
        i = 0
        for k, icon in icons.items():
            if k in ['tianchong', 'border']:
                self.btns[k] = ttk.Button(toolframe, image=icon, command=functools.partial(self.choose_color, _type=k))
            elif 'bold' == k:
                lb = tk.Label(toolframe, text='粗细:', font=('文泉驿微米黑', 10), bg="white")
                lb.pack(side=tk.LEFT, padx=2, pady=1)
                self.btns[k] = ttk.Spinbox(toolframe, values=list(range(1, 9, 1)),
                                    textvariable = self.border, width=2)
            else:
                self.btns[k] = ttk.Button(toolframe, image=icon, command=functools.partial(self.btn_event, _type=k))
            self.btns[k].pack(side=tk.LEFT, padx=2, pady=1)
            i += 1

    def btn_event(self, _type='line'):
        """按钮处理函数，切换绘制图形"""
        self.clear_polygon_point()
        self.cur_drawing = _type
        print(_type)

    def choose_color(self, _type):
        """针对填充、边框，创建颜色选择对话框"""
        if 'border' == _type:
            self.border_color = colorchooser.askcolor(parent=self.mw, title='选择颜色', color = 'black')[1]
        elif 'tianchong' == _type:
            self.fill_color = colorchooser.askcolor(parent=self.mw, title='选择颜色', color = 'black')[1]

    def mouse_mid(self, event):
        """鼠标中间按住拖动处理函数，用户移动图像"""
        if not self.move_cvs:
            self.move_cvs = self.cv.find_closest(event.x, event.y)
        if self.x_pos < 0:
            self.x_pos = event.x
        if self.y_pos < 0:
            self.y_pos = event.y
        for cvid in self.move_cvs:
            self.cv.move(cvid, event.x - self.x_pos, event.y - self.y_pos)
        self.x_pos, self.y_pos = event.x, event.y

    def mouse_mid_release(self, event):
        """鼠标中间释放处理函数，移动图像结束，清理"""
        self.move_cvs = []
        self.x_pos, self.y_pos = -1, -1

    def clear_polygon_point(self):
        """清理多边形点坐标"""
        self.pointer_coordinate = []
        [self.cv.delete(cv_id) for cv_id in self.pointer]
        self.pointer = []

    def mouse_click(self, event):
        """右击事件，用于：
            1. 多边形绘制，标定节点
            2. 橡皮擦功能，删除指定图像
        """
        if 'dbx' == self.cur_drawing:
            # 多边形绘制，标定节点
            if len(self.pointer_coordinate) > 3 and \
                get_point_distance(self.pointer_coordinate[0], (event.x, event.y)) < 10:
                self.cv.create_polygon(*self.pointer_coordinate, outline=self.border_color, width=self.border.get(), fill=self.fill_color)
                self.clear_polygon_point()
            else:
                if self.pointer_coordinate:
                    self.pointer.append(self.cv.create_line(self.pointer_coordinate[-1][0], self.pointer_coordinate[-1][1],
                                                event.x, event.y, width=self.border.get(), fill=self.border_color))
                self.pointer_coordinate.append((event.x, event.y))
                # 画点
                self.pointer.append(self.cv.create_rectangle(event.x, event.y, event.x+4,
                                                event.y+4, outline=None, fill=self.fill_color))
        elif 'xiangpi' == self.cur_drawing:
            # 橡皮擦功能，删除指定图像
            [self.cv.delete(cv_id) for cv_id in self.cv.find_closest(event.x, event.y)]
            self.clear_polygon_point()
        else:
            self.clear_polygon_point()

    def mouse_move(self, event):
        """鼠标右键按住移动处理函数，用于确定图像起始点、大小、方位等"""
        if self.x_pos < 0:
            self.x_pos = event.x
        if self.y_pos < 0:
            self.y_pos = event.y
        self.cur_x_pos, self.cur_y_pos = event.x, event.y
        if self.temp_cv:
            self.cv.delete(self.temp_cv)
        if 'juxing' == self.cur_drawing:
            self.temp_cv = self.cv.create_rectangle(self.x_pos, self.y_pos, self.cur_x_pos,
                                                    self.cur_y_pos, width=2, outline='#2f4f4f', dash=15)
        elif 'tuoyuan' == self.cur_drawing:
            self.temp_cv = self.cv.create_oval(self.x_pos, self.y_pos, self.cur_x_pos,self.cur_y_pos,
                                                    width=2, outline='#2f4f4f', dash=15)
        elif 'line' == self.cur_drawing:
            self.temp_cv = self.cv.create_line(self.x_pos, self.y_pos, self.cur_x_pos,self.cur_y_pos,
                                                    width=self.border.get(), fill=self.border_color)
        elif 'pencil' == self.cur_drawing:
            self.cv.create_line(self.x_pos, self.y_pos, self.cur_x_pos,self.cur_y_pos, width=self.border.get(), fill=self.border_color)
            self.x_pos, self.y_pos = self.cur_x_pos,self.cur_y_pos

    def mouse_release(self, event):
        """鼠标右键释放处理函数，用于确定图像起始点、大小、方位，以及收尾工作"""
        if 'juxing' == self.cur_drawing:
            self.cv.create_rectangle(self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos,
                                        outline=self.border_color, width=self.border.get(), fill=self.fill_color)
        elif 'tuoyuan' == self.cur_drawing:
            self.cv.create_oval(self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos,
                                        outline=self.border_color, width=self.border.get(), fill=self.fill_color)
        elif 'line' == self.cur_drawing:
            self.cv.create_line(self.x_pos, self.y_pos, self.cur_x_pos,self.cur_y_pos,
                                    width=self.border.get(), fill=self.fill_color)
        if self.temp_cv:
            self.cv.delete(self.temp_cv)
        self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos = -1, -1, -1, -1


if __name__ == "__main__":
    mw = tk.Tk()
    mw.title("雷那画板 - www.tpleina.com")
    mw.iconbitmap('image/logo.ico')
    mw.geometry("600x400+400+100")
    Drawer(mw)
    mw.mainloop()

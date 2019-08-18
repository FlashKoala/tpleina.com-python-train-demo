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
import os
import time
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from PIL import ImageGrab, ImageTk


# 获得桌面路径
get_desktop_path = lambda :os.path.join(os.path.expanduser("~"), 'Desktop')
IMAGE_TYPES = [("PNG格式", "*.png"), ('JPG格式', '*.jpg')]
# image 实例对象
GRAB_IMG = None

class Screen(object):
    def __init__(self, mw):
        self.mw = mw
        self.x_pos,self.y_pos = -1, -1
        self.cur_x_pos, self.cur_y_pos = -1, -1
        # 状态标记位：是否有框选图形
        # cavans框选图形tag
        self.selected = "capture"
        # cavans引导线tag
        self.guideline = "guideline"
        # 区域截屏坐标
        self.grab_point = []
        self.init_widgets()
        self.screen.wait_window(self.screen)

    def init_widgets(self):
        # 显示宽度px
        self.width = mw.winfo_screenwidth()
        # 显示高度px
        self.height = mw.winfo_screenheight()
        # 创建窗口
        self.screen = tk.Toplevel(mw, width=self.width, height=self.height)
        # 设置模式对话框
        self.screen.grab_set()
        # 去掉窗口标题栏、边框等
        self.screen.overrideredirect(True)
        # 窗口获取焦点
        self.screen.focus_set()
        # 初始化canvas
        self.cv = tk.Canvas(self.screen, width=self.width, height=self.height)
        self.cv.pack(fill=tk.BOTH, expand=tk.YES)
        # 全屏截屏
        im = ImageGrab.grab((0, 0, self.width, self.height))
        self.cv.im = ImageTk.PhotoImage(im)
        self.cv.create_image(0, 0, image=self.cv.im, anchor=tk.NW)
        # esc键，退出截屏
        self.screen.bind('<Escape>', self.destroy)
        # 双击，退出截屏
        self.screen.bind('<Double-1>', self.destroy)
        # 鼠标移动事件
        self.cv.bind('<Motion>', self.mouse_move)
        # 右键按住移动事件
        self.cv.bind('<B1-Motion>', self.mouse_press_move)
        # 右键释放事件
        self.cv.bind('<ButtonRelease-1>', self.mouse_release)

    def do_grab(self):
        """区域截屏"""
        global GRAB_IMG
        if len(self.grab_point) == 4:
            self.grab_point[0], self.grab_point[2] = (self.grab_point[2], self.grab_point[0]) if self.grab_point[0] > self.grab_point[2] \
                else (self.grab_point[0], self.grab_point[2])
            self.grab_point[1], self.grab_point[3] = (self.grab_point[3], self.grab_point[1]) if self.grab_point[1] > self.grab_point[3] \
                else (self.grab_point[1], self.grab_point[3])
            GRAB_IMG = ImageGrab.grab(self.grab_point)
            self.grab_point = []

    def mouse_move(self, event):
        """鼠标移动处理函数，用于绘制区域截图辅助线"""
        self.cv.delete(self.guideline)
        self.cv.create_line(event.x, 0, event.x, self.height, fill='#2780E3', dash=20, tag=self.guideline)
        self.cv.create_line(0, event.y, self.width, event.y, fill='#2780E3', dash=20, tag=self.guideline)

    def mouse_press_move(self, event):
        """鼠标右键按住移动处理函数，用于确定图像起始点、大小、方位等"""
        if self.x_pos < 0:
            self.x_pos = event.x
            self.grab_point = [self.x_pos, -1, self.x_pos, -1]
        if self.y_pos < 0:
            self.y_pos = event.y
            self.grab_point[1] = self.y_pos
        self.grab_point[2] = self.cur_x_pos
        self.grab_point[3] = self.cur_y_pos
        self.cur_x_pos, self.cur_y_pos = event.x, event.y
        self.cv.delete(self.selected)
        self.cv.create_rectangle(self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos,
                                                width=2, outline='#2780E3', dash=20, tag=self.selected)
    def mouse_release(self, event):
        """鼠标右键释放处理函数
           1. 用于确定图像起始点、大小、方位
           2. 触发区域截屏
           3. 对话框自清理
        """
        self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos = -1, -1, -1, -1
        self.do_grab()
        self.destroy()

    def destroy(self, event=None):
        """析构函数"""
        self.screen.withdraw()
        self.screen.update_idletasks()
        self.screen.destroy()


class ScreenCapture(object):
    def __init__(self, mw):
        self.mw = mw
        self.s = ttk.Style()
        # 右键菜单项
        self.options = ['保存']
        # 状态,是否加载图片
        self.has_img = False
        self.initWidgets()

    def initWidgets(self):
        # 图片显示区
        self.sf = ttk.Frame(self.mw)
        self.sf.pack(fill=tk.BOTH)
        self.label = ttk.Label(self.sf)
        self.label.pack()
        # 创建右键菜单
        self.right_menu = tk.Menu(self.mw, tearoff = 0)
        for item in self.options:
            # 添加项
            self.right_menu.add_command(label=item, command=self.save_event)
        self.label.bind('<Button-3>', self.popup)
        # 操作区
        self.s.configure('C.TButton', width=6)
        self.cf = ttk.Frame(self.mw)
        self.cf.pack(fill=tk.BOTH,pady=4)
        # 截屏按钮
        self.btn = ttk.Button(self.cf, text='截屏', command=self.capture, style='C.TButton')
        self.btn.pack(side=tk.BOTTOM)
    
    def show(self):
        global GRAB_IMG
        if GRAB_IMG:
            self.sf.im = ImageTk.PhotoImage(GRAB_IMG)
            self.label['image'] = self.sf.im
            self.has_img = True
        
    def capture(self):
        """截屏处理函数"""
        global GRAB_IMG
        GRAB_IMG = None
        # 窗口最小化
        self.mw.state('icon')
        time.sleep(0.4)
        Screen(self.mw)
        # 窗口恢复
        self.mw.state('normal')
        # 获得焦点
        self.mw.focus_set()
        # 显示截图
        self.show()

    def popup(self, event):
        """右键菜单事件处理函数"""
        if self.has_img:
            # 有图片执行动作
            self.right_menu.post(event.x_root,event.y_root)

    def save_event(self):
        """保存图片事件处理函数"""
        global GRAB_IMG
        # 保存文件对话框
        filep = filedialog.asksaveasfilename(title='保存图片',
                                        initialdir=get_desktop_path(),
                                        filetypes=IMAGE_TYPES)
        if filep:
            if not "png" == filep.split(".")[-1].lower().strip():
                filep += ".png"
            GRAB_IMG.save(filep)
            messagebox.showinfo("消息提示", "图片保存成功！", icon="info", type="ok")


if __name__ == "__main__":
    mw = tk.Tk()
    mw.title("雷那截图工具 - www.tpleina.com")
    mw.iconbitmap('asset/logo.ico')
    mw.resizable(False, False)
    ScreenCapture(mw)
    mw.mainloop()

# -*- coding:utf-8 -*-
# Copyright 2019 by www.tpleina.com. All Rights Reserved.
#
#
##################################################
######## Please Don't Remove Author Name #########
############### Thanks ###########################
##################################################
#
#
"""
Copyright (C) 2019 www.tpleina.com. All Rights Reserved.
Author: Flash Koala
Contact: tpleina@qq.com
"""
__author__='''
######################################################
Copyright (C) 2019 www.tpleina.com. All Rights Reserved.                       
######################################################
    Flash Koala
    http://www.tpleina.com  
    雷那网 - 一个有温度的Python兴趣屋！
######################################################
'''

__version__ = "1.0.0"
from collections import OrderedDict
import json
import functools
import os
import sys
from io import BytesIO
import tkinter as tk
from tkinter import ttk,colorchooser,filedialog,messagebox

from aip import AipOcr
from PIL import Image,ImageGrab, ImageTk


APP_ID = ''
API_KEY = ''
SECRET_KEY = ''

# 获得桌面路径
get_desktop_path = lambda :os.path.join(os.path.expanduser("~"), 'Desktop')
# 获得windows临时目录
get_os_temppath = lambda :os.path.join(os.path.expanduser("~"), 'AppData/Local')
APP_TMP_PATH = os.path.join(get_os_temppath(), "wwwleinacom")
# 配置文件名
SETTING_FILE = 'setting.json'
IMAGE_TYPES = [("PNG格式", "*.png"), ('JPG格式', '*.jpg')]


def gen_dialog_box(msg, _type="Info"):
    """生产对话框"""
    if "Info" == _type:
        messagebox.showinfo("消息提示", msg, icon="info", type="ok")
    elif "Warning" == _type:
        messagebox.showwarning("告警信息", msg, icon="warning", type="ok")
    elif "Error" == _type:
        messagebox.showwarning("告警信息", msg, icon="error", type="ok")


# 资源文件目录
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class KeyDialog(tk.Toplevel):
    """设置APIKEY对话框"""
    def __init__(self, parent, title=None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.parent = parent
        # 设置标题
        if title: self.title(title)
        self.iconbitmap(resource_path('asset/logo.ico'))
        # 设置模式对话框
        self.grab_set()
        tokens = json.loads(open(APP_TMP_PATH + "/" + SETTING_FILE, 'r').read())
        self.app_id = tk.StringVar(value=tokens.get("APP ID", ""))
        self.api_key = tk.StringVar(value=tokens.get("API KEY", ""))
        self.sec_key = tk.StringVar(value=tokens.get("SECRET KEY", ""))
        self.initWidgets()
    
    def initWidgets(self):
        # 创建对话框主体内容
        uf = ttk.Frame(self)
        # 创建并添加Label
        ttk.Label(uf, text='APP ID: ').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(uf, textvariable=self.app_id).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(uf, text='API KEY: ').grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(uf, textvariable=self.api_key).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(uf, text='SECRET KEY: ').grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(uf, textvariable=self.sec_key).grid(row=2, column=1, padx=5, pady=5)
        uf.pack()
        df = ttk.Frame(self)
        # 保存按钮
        ttk.Button(df, text="保存", width=10, command=self.ok_click, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        # 取消按钮
        ttk.Button(df, text="取消", width=10, command=self.cancel_click).pack(side=tk.LEFT, padx=5, pady=5)
        # 绑定事件处理方法
        self.bind("<Return>", self.ok_click)
        self.bind("<Escape>", self.cancel_click)
        df.pack()
        # 窗口被关闭，调用self.cancel_click方法
        self.protocol("WM_DELETE_WINDOW", self.cancel_click)
        # 根据父窗口来设置对话框的位置
        self.geometry("+%d+%d" % (self.winfo_rootx() + 150, self.winfo_rooty() + 200))
        self.wait_window(self)
    
    def validate(self):
        """校验输入数据有效性"""
        if not (self.api_key.get() and self.sec_key.get() and self.app_id.get()):
            gen_dialog_box("内容不完整", "Warning")
            return False
        return True
    
    def ok_click(self, event=None):
        # 校验用户输入
        if not self.validate():
            return
        with open(APP_TMP_PATH + "/" + SETTING_FILE, 'w') as f:
            f.write(json.dumps(
                {
                    'APP ID': self.app_id.get(),
                    'API KEY': self.api_key.get(),
                    'SECRET KEY': self.sec_key.get()
                },
                indent=2
            ))
        self.withdraw()
        self.update_idletasks()
        # 将焦点返回给父窗口
        self.parent.focus_set()
        # 销毁窗口
        self.destroy()

    def cancel_click(self, event=None):
        # 将焦点返回给父窗口
        self.parent.focus_set()
        # 销毁窗口
        self.destroy()


class GuiOcr(object):
    """文字提取实现类
    """
    def __init__(self, mw):
        self.mw = mw
        self.tokens = json.loads(open(APP_TMP_PATH + "/" + SETTING_FILE, 'r').read())
        self.initWidgets()

    def initWidgets(self):
        # 初始参数
        self.img_tag = "img"
        self.has_img = False
        self.x_pos, self.y_pos = -1, -1
        self.cur_x_pos, self.cur_y_pos = -1, -1
        self.pointer = []
        # 选择绘制图像
        self.cur_tool = 'juxing'
        self.seleted_tag = 'selected'
        # 初始化图标
        self.init_icons()
        # 初始化工具条
        self.init_toolbar()
        # 初始化主面板Frame容器
        self.init_mainboard()

    def init_mainboard(self):
        """显示区"""
        self.mf = ttk.Frame(self.mw)
        self.mf.pack(fill=tk.BOTH, expand=tk.YES)
        self.cv = tk.Canvas(self.mf, background='white', height=100)
        self.cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        # 导入图片
        self.cv.bind("<Double-1>", self.load_img)
        # 右键按住移动事件
        self.cv.bind('<B1-Motion>', self.mouse_move)
        # 右键释放事件
        self.cv.bind('<ButtonRelease-1>', self.mouse_release)
        # # 鼠标中间按住拖动，用于移动图形
        self.cv.bind('<B2-Motion>', self.mouse_mid)
        # 画布绑定滚动条
        self.scr1 = tk.Scrollbar(self.mf, command=self.cv.yview)
        self.cv.configure(yscrollcommand=self.scr1.set)
        self.scr1.pack(side=tk.LEFT, fill=tk.Y)

        self.lf = ttk.LabelFrame(self.mw, text='内容输出')
        self.lf.pack(fill=tk.BOTH, expand=tk.YES)
        self.text = tk.Text(self.lf, font=('宋体', 12), height=4)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        # 为输入文本框绑定滚动条
        self.scroll = tk.Scrollbar(self.lf, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=tk.LEFT, fill=tk.Y)

    def init_icons(self):
        """初始化图标"""
        self.mw.xiangpi_icon = tk.PhotoImage(file='asset/xiangpi.png')
        self.mw.juxing_icon = tk.PhotoImage(file='asset/juxing.png')
        self.mw.open_icon = tk.PhotoImage(file='asset/open.png')
        self.mw.find_icon = tk.PhotoImage(file='asset/find.png')
        self.mw.setting_icon = tk.PhotoImage(file='asset/setting.png')

    def init_toolbar(self):
        """创建窗口工具栏菜单"""
        self.btns = {}
        toolframe = tk.Frame(self.mw, height=40, bg='white')
        toolframe.pack(fill=tk.X)
        icons = {'open': self.mw.open_icon, # 打开
                    'juxing': self.mw.juxing_icon, # 矩形工具
                    'xiangpi': self.mw.xiangpi_icon, # 橡皮
                    'find': self.mw.find_icon, # 识别
                    'setting': self.mw.setting_icon
                    }        
        for k, icon in icons.items():
            self.btns[k] = ttk.Button(toolframe, image=icon, command=functools.partial(self.btn_event, _type=k))
            self.btns[k].pack(side=tk.LEFT, padx=2, pady=1)

    def btn_event(self, _type='juxing'):
        """按钮处理函数，切换绘制图形"""
        self.cur_tool = _type
        print(_type)
        if "open" == _type:
            self.load_img()
        elif "xiangpi" == _type:
            self.cv.delete(self.seleted_tag)
        elif "find" == _type:
            self.capture()
        elif "setting" == _type:
            KeyDialog(self.mw, title='ADD API KEY')

    def load_img(self, event=None):
        """打开图片事件处理函数"""
        self.cv.delete(self.seleted_tag)
        # 导入图片并显示
        imgp = filedialog.askopenfilename(title='导入图片',
                                            filetypes=IMAGE_TYPES,
                                            initialdir=get_desktop_path())
        if imgp:
            self.show_img(imgp)

    def reset_canvas_size(self):
        """根据图片大小，重置画布尺寸"""
        self.cv.update()
        self.cv['width'], self.cv['height'] = self.img_w, self.img_h
        print('cv size:', self.cv['width'], self.cv['height'])
        self.cv.update()

    def show_img(self, imgp):
        """图片显示"""
        # 校验图片格式
        try:
            self.im = Image.open(imgp)
            self.cv.im = ImageTk.PhotoImage(self.im)
        except:
            gen_dialog_box("非图片格式!","Error")
            return
        self.img_w, self.img_h = self.im.size[0], self.im.size[1]
        # 重置画布尺寸
        self.reset_canvas_size()
        # 绘制图片
        self.cv.create_image(0, 0, image=self.cv.im, anchor=tk.NW, tag=self.img_tag)
        self.has_img = True
        print('cv size:', self.cv['width'], self.cv['height'])
        self.cv.update()
        self.cur_tool = 'juxing'

    def mouse_move(self, event):
        print(event.x, event.y)
        """鼠标右键按住移动处理函数，绘制矩形选框"""
        if not self.has_img:
            return
        if not self.cur_tool == 'juxing':
            return
        self.cv.delete(self.seleted_tag)
        if self.x_pos < 0:
            self.x_pos = event.x
        if self.y_pos < 0:
            self.y_pos = event.y
        self.cur_x_pos, self.cur_y_pos = event.x, event.y
        self.cv.create_rectangle(self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos,
                                    width=2, outline='#007ACC', tag=self.seleted_tag)

    def mouse_release(self, event):
        if not self.has_img:
            return
        if not self.cur_tool == 'juxing':
            return
        if self.cv.find_withtag(self.seleted_tag):
            self.pointer = [
                self.x_pos, self.y_pos,
                self.cur_x_pos, self.cur_y_pos
            ]
            self.x_pos, self.y_pos, self.cur_x_pos, self.cur_y_pos = -1, -1, -1, -1
                      
    def mouse_mid(self, event):
        """鼠标中间按住拖动处理函数，移动选框"""
        if not self.has_img:
            return
        if self.x_pos < 0:
            self.x_pos = event.x
        if self.y_pos < 0:
            self.y_pos = event.y
        self.cv.move(self.seleted_tag, event.x - self.x_pos, event.y - self.y_pos)
        self.x_pos, self.y_pos = event.x, event.y

    def mouse_mid_release(self, event):
        """鼠标中间释放处理函数，移动图像结束"""
        self.x_pos, self.y_pos = -1, -1

    def capture(self):
        if len(self.pointer) != 4:
            return
        if -1 in self.pointer:
            return
        if len(set(self.tokens.values())) != 3:
            self.tokens = json.loads(open(APP_TMP_PATH + "/" + SETTING_FILE, 'r').read())
            if len(set(self.tokens.values())) != 3:
                gen_dialog_box("请设置API KEY", "Warning")
                return
        if self.pointer[0] > self.pointer[2]:
            self.pointer[0], self.pointer[2] = self.pointer[2], self.pointer[0]
        if self.pointer[1] > self.pointer[3]:
            self.pointer[1], self.pointer[3] = self.pointer[3], self.pointer[1]
        im = self.im.crop(self.pointer)
        out = BytesIO()
        im.save(out,'png')
        out.seek(0)
        res = AipOcr(self.tokens.get('APP ID'), self.tokens.get('API KEY'), self.tokens.get('SECRET KEY')).basicAccurate(out.read())
        if not res.get("words_result", []):
            gen_dialog_box("未发现文字!")
        else:
            texts = map(lambda x: x.get("words"), res.get("words_result", []))
            self.text.delete(1.0, tk.END)
            self.text.insert(1.0, "\n".join(texts))


def main():
    # 配置文件不存在，则创建配置文件
    if not os.path.exists(APP_TMP_PATH + "/" + SETTING_FILE):
        with open(APP_TMP_PATH + "/" + SETTING_FILE, 'w') as f:
            f.write(json.dumps({}))

    mw = tk.Tk()
    mw.title("雷那文体提取工具 - www.tpleina.com")
    mw.iconbitmap('asset/logo.ico')
    GuiOcr(mw)
    mw.mainloop()


if __name__ == "__main__":
    main()


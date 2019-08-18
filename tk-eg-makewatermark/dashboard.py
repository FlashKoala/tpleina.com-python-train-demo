# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox,colorchooser,filedialog

from conf import CONF
from util import get_desktop_path, gen_dialog_box

class DashBoard(object):
    """工具操作区类"""
    def __init__(self, mw):
        self.mw = mw
        # 默认水印颜色
        self.df_clr = tk.StringVar()
        self.df_clr.set('black')
        # 水印文字
        self.text_var = tk.StringVar()
        self.text_var.set(CONF.INIT_MARK_TEXT)
        # 字体大小
        self.fs_var = tk.IntVar()
        self.fs_var.set(14)
        # 水印模式
        self.sy_val = tk.StringVar()
        self.sy_val.set('left-down')
        self.init()

    def init(self):
        # 主操作区
        self.mlf = ttk.LabelFrame(self.mw, text='操作区')
        self.mlf.pack(fill=tk.BOTH, expand=tk.YES, padx=4, pady=5, ipadx=4, ipady=10)
        # 左侧操作区 
        self.cf = ttk.Frame(self.mlf)
        self.cf.pack(side=tk.LEFT,fill=tk.X,padx=4,expand=tk.YES)
        ttk.Button(self.cf, text="导入图片",command=self.load_img).pack(fill=tk.BOTH, expand=True)
        ttk.Button(self.cf, text="生成水印",command=self.gen_mark).pack(fill=tk.BOTH, expand=True)
        # 右侧编辑区 
        self.ef = ttk.Frame(self.mlf)
        self.ef.pack(side=tk.LEFT,fill=tk.X,padx=10,expand=tk.YES)
        # 水印输入框
        self.text = ttk.Entry(self.ef, textvariable=self.text_var)
        self.text.pack(padx=20, pady=4, fill=tk.BOTH, expand=True)
        # 大小选择组件
        ttk.Label(self.ef, text='大小:').pack(side=tk.LEFT,padx=2,fill=tk.X, expand=tk.YES)
        self.sbox2 = ttk.Spinbox(self.ef, width=3,from_=CONF.MIN_FONT_SIZE, to=CONF.MAX_FONT_SIZE,
                                    increment=2, textvariable=self.fs_var)
        self.sbox2.pack(side=tk.LEFT,padx=2,fill=tk.X, expand=tk.YES)
        # 颜色选择组件
        ttk.Button(self.ef, text="颜色",command=self.choose_color).pack(side=tk.LEFT,padx=5,fill=tk.X)
        # 水印模式,单选按钮组
        for p in CONF.MARK_MODES:
            ttk.Radiobutton(self.ef,
                text = p[1],
                variable = self.sy_val,
                value=p[0]).pack(side=tk.LEFT,fill=tk.X)
    
    def get_text(self):
        """获得水印文字"""
        return self.text_var.get()
    
    def set_text(self, text):
        """设置水印文字"""
        self.text_var.set(text)

    def get_font_size(self):
        """获取水印文字大小"""
        return self.fs_var.get()

    def set_font_size(self, size):
        """设置水印文字大小"""
        self.fs_var.set(size)

    def get_font_color(self):
        """获得水印文字颜色"""
        return self.df_clr.get()

    def set_font_color(self, clr):
        """设置水印文字"""
        return self.df_clr.set(clr)

    def get_mark_mode(self):
        """获得水印模式"""
        return self.sy_val.get()

    def set_mark_mode(self, mode):
        """设置水印模式"""
        self.sy_val.set(mode)

    def choose_color(self):
        """选择颜色,事件处理函数"""
        clr_v = colorchooser.askcolor(parent=self.mw, title='选择颜色')
        if clr_v[1]:
            self.df_clr.set(clr_v[1])

    def add_screen(self, scr):
        """引用显示屏幕类实例"""
        self.scr = scr

    def load_img(self):
        """导入图片,事件处理函数"""
        imgp = filedialog.askopenfilename(title='导入图片',
                                            filetypes=CONF.IMAGE_TYPES,
                                            initialdir=get_desktop_path())
        self.scr.show_img(imgp)
    
    def get_win_size(self):
        """获得操作区组件长宽"""
        self.mlf.update()
        return self.mlf.winfo_width(), self.mlf.winfo_height()

    def validate(self):
        """校验数据有效性"""
        if len(self.get_text()) > CONF.MAX_MARK_LEN:
            gen_dialog_box("水印内容超过%d长度!" % (CONF.MAX_MARK_LEN), "Warning")
            return False
        if len(self.get_text()) < 1:
            gen_dialog_box("请输入水印内容!", "Warning")
            return False
        if self.get_font_size() > CONF.MAX_FONT_SIZE:
            gen_dialog_box("水印字体大小超过%d!" % (CONF.MAX_FONT_SIZE), "Warning")
            return False
        if self.get_font_size() < CONF.MIN_FONT_SIZE:
            gen_dialog_box("水印字体大小小于%d!" % (CONF.MIN_FONT_SIZE), "Warning")
            return False
        return True

    def gen_mark(self):
        """添加水印,事件处理函数"""
        if not self.validate():
            return
        self.scr.add_mark(
            self.get_text(),
            self.get_font_size(),
            self.get_font_color(),
            self.get_mark_mode()
        )

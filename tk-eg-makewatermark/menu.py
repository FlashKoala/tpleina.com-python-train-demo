# -*- coding:utf-8 -*-
import json
import os
import tinify
import tkinter as tk
from tkinter import Tk,ttk,messagebox, colorchooser,filedialog

from conf import CONF
from util import get_desktop_path, gen_dialog_box,resource_path


CONFP = os.path.join(CONF.APP_TMP_PATH, CONF.SETTINGS)
APIKEY = ""

def get_apikey():
    """获得APIKEY"""
    return APIKEY

def set_apikey(apikey):
    """设置APIKEY"""
    global APIKEY
    APIKEY = apikey

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
        self.key_text = tk.StringVar()
        self.key_text.set(APIKEY)
        self.initWidgets()
    
    def initWidgets(self):
        # 创建对话框主体内容
        uf = ttk.Frame(self)
        # 创建并添加Label
        ttk.Label(uf, text='API TOKEN: ').pack(side=tk.LEFT, padx=5, pady=5)
        self.name_entry = ttk.Entry(uf, textvariable=self.key_text).pack(side=tk.LEFT, padx=5, pady=5)
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
        if len(self.key_text.get()) > 100:
            gen_dialog_box("API TOKEN 不超过100个字符", "Warning")
            return False
        return True
    
    def ok_click(self, event=None):
        # 校验用户输入
        if not self.validate():
            return
        global APIKEY
        APIKEY = self.key_text.get()
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


class WinMenu(object):
    """工具菜单类"""
    def __init__(self, mw, winsty):
        self.mw = mw
        self.winsty = winsty
        self.theme = tk.StringVar()
        self.is_compress = tk.IntVar()
        self.theme.set("vista")
        self.is_compress.set(0)
        self.init_menu()

    def init_menu(self):
        menubar = tk.Menu(self.mw)
        # 将menu设置为窗口的菜单条
        self.mw['menu'] = menubar
        # 创建文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        # 将文件菜单加入菜单条
        menubar.add_cascade(label='文件', menu=file_menu)
        # 添加菜单项
        file_menu.add_command(label="打开", command=self.load_img, compound=tk.LEFT)
        # 添加菜单项
        file_menu.add_command(label="压缩KEY", command=self.add_apikey, compound=tk.LEFT)
        # 添加分隔条
        file_menu.add_separator()
        # 创建主题子菜单
        theme_menu = tk.Menu(file_menu, tearoff=0)
        # 添加子菜单
        file_menu.add_cascade(label='选择主题', menu=theme_menu)
        # 主题子菜单添加菜单项
        for im in CONF.THEMES:
            theme_menu.add_radiobutton(label=im[1],
                                        command=self.choose_theme,
                                        variable=self.theme,
                                        value=im[0])
        # 添加分隔条
        file_menu.add_separator()
        # 创建子菜单
        sub_menu = tk.Menu(file_menu, tearoff=0)
        # 添加sub_menu子菜单
        file_menu.add_cascade(label='是否压缩', menu=sub_menu)
        # 为sub_menu子菜单添加菜单项
        for im in [(1, '是'), (0, '否')]:
            sub_menu.add_radiobutton(label=im[1], command=None, variable=self.is_compress, value=im[0])
        # 添加分隔条
        file_menu.add_separator()
        # 添加菜单项
        file_menu.add_command(label="关于", command=self.open_about, compound=tk.LEFT)

    def add_screen(self, scr):
        """引入屏幕显示类实例"""
        self.scr = scr

    def set_iscompress(self, iscompress=1):
        """设置压缩"""
        self.is_compress.set(iscompress)
    
    def get_iscompress(self):
        """获取压缩状态"""
        return self.is_compress.get()

    def iscompress(self):
        """是否压缩"""
        return 1 == self.is_compress.get()

    def set_theme(self, theme):
        """设置主题样式"""
        self.theme.set(theme)
    
    def get_theme(self):
        """获取当前主题样式"""
        return self.theme.get()

    def choose_theme(self):
        """选择主题事件处理函数"""
        print(self.theme.get())
        self.winsty.theme_use(self.theme.get())

    def load_img(self):
        """打开图片事件处理函数"""
        # 导入图片并显示
        imgp = filedialog.askopenfilename(title='导入图片',
                                            filetypes=CONF.IMAGE_TYPES,
                                            initialdir=get_desktop_path())
        self.scr.show_img(imgp)

    def open_about(self):
        """打开关于对话框处理函数"""
        gen_dialog_box("""水印生成工具由雷那网制作提供\n该软件工具版权归雷那网所有！\n欢迎登陆雷那网 - www.tpleina.com 了解Python技术！
        """)

    def add_apikey(self):
        """添加设置APIKEY事件处理函数"""
        KeyDialog(self.mw, title='填写图片压缩API TOKEN')

    def make_compress_img(self, buffer_img, imgp):
        """压缩图片文件事件处理函数"""
        global APIKEY
        tinify.key = APIKEY
        tinify.from_buffer(buffer_img).to_file(imgp)

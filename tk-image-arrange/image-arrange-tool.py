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
import tkinter as tk
from tkinter import ttk,filedialog,colorchooser
from tkinter import messagebox as msgbox
import os

from PIL import Image, ImageTk


# 窗口宽度和高度
WIN_WIDTH, WIN_HEIGHT = 700, 500


class ImageGui(object):
    """图片分类工具实现类
    """
    def __init__(self, mw):
        self.mw = mw
        # 工具按钮对象
        self.btns = {}
        # 工作模式：
        # move - 默认模式，图片移动
        # copy - 图片复制
        self.mode = "move"
        # 添加分类目录，保存在有序字典中
        self.sub_dirs = OrderedDict()
        # 选中分类目录集合
        self.selected_path = []
        # 有效图片格式
        self.image_pattern = ['png', 'jpg', 'jpeg']
        # 图片集合
        self.images = []
        # 上一个/下一个，记录位置
        self.step = 0
        # 状态栏信息提示
        self.tip = tk.StringVar()
        self.tip.set("雷那网 - www.tpleina.com |图片: {}/0|工作模式: {}".format(len(self.images), self.mode))
        # 打开的图片对象
        self.org_im = None
        # 初始化窗口
        self.initWidgets()

    def initWidgets(self):
        # 初始化图标
        self.init_icons()
        # 调用init_toolbar初始化工具条
        self.init_toolbar()
        # 初始化主面板Frame容器
        self.init_mainboard()

    def init_icons(self):
        """初始化图标"""
        self.mw.open_icon = tk.PhotoImage(file='image/open.png')
        self.mw.adddir_icon = tk.PhotoImage(file='image/adddir.png')
        self.mw.copy_icon = tk.PhotoImage(file='image/copy.png')
        self.mw.move_icon = tk.PhotoImage(file='image/move.png')
        self.mw.pre_icon = tk.PhotoImage(file='image/pre.png')
        self.mw.next_icon = tk.PhotoImage(file='image/next.png')
        self.mw.zhixing_icon = tk.PhotoImage(file='image/zhixing.png')

    def init_toolbar(self):
        """创建窗口工具栏菜单"""
        toolframe = tk.Frame(self.mw, height=42, bg='white')
        toolframe.pack(fill=tk.X)
        icons = {'open': (self.mw.open_icon, self.open_imgdir), # 打开图片文件夹
                    'addir': (self.mw.adddir_icon, self.add_subdir), # 添加子目录
                    'copy': (self.mw.copy_icon, functools.partial(self.switch_mode, mode='copy')), # 复制图片
                    'move': (self.mw.move_icon, self.switch_mode) # 移动图片
                    }
        i = 0
        for k, icon in icons.items():
            self.btns[k] = ttk.Button(toolframe, image=icon[0], command=icon[1])
            self.btns[k].pack(side=tk.LEFT, padx=2, pady=1)
            i += 1

    def init_mainboard(self):
        """主窗口"""
        self.mf = ttk.Frame(self.mw)
        self.mf.pack(fill=tk.BOTH, expand=True)

        self.cf = ttk.Frame(self.mf)
        self.cf.pack(fill=tk.BOTH, expand=True)
        # 窗口状态栏
        self.status_label = tk.Label(self.mf, textvariable=self.tip)
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH)
        # 右侧操作区
        self.oplf = ttk.LabelFrame(self.cf, text='分类目录')
        self.oplf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES, pady=2)
        # 左侧图片显示组件
        self.screenlf = ttk.LabelFrame(self.cf, text='图片显示 - 缩略图', padding=20)
        self.screenlf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES, pady=2, padx=2)
        self.cv = tk.Canvas(self.screenlf, width=WIN_WIDTH-200, height=WIN_HEIGHT-140)
        self.cv.pack()
        # 右上侧分类目录显示区
        self.dirlf = ttk.Frame(self.oplf)
        self.dirlf.pack(fill=tk.BOTH)
        self.btnlf = ttk.Frame(self.oplf)
        self.btnlf.pack(side=tk.BOTTOM, fill=tk.BOTH, anchor=tk.S)
        # 右下方按钮区
        self.btn_pre = ttk.Button(self.btnlf, image=self.mw.pre_icon, command=functools.partial(self.browse_image, direct='down'))
        self.btn_pre.pack(side=tk.LEFT, expand=True)
        self.btn_next = ttk.Button(self.btnlf, image=self.mw.next_icon, command=functools.partial(self.browse_image, direct='up'))
        self.btn_next.pack(side=tk.LEFT, expand=True)
        self.btn_zhixing = ttk.Button(self.btnlf, image=self.mw.zhixing_icon, command=self.do_image_arrange)
        self.btn_zhixing.pack(side=tk.RIGHT, expand=True)

    def show_sub_dir(self):
        """分类目录显示"""
        idx = 0
        for path, var in self.sub_dirs.items():
            ttk.Label(self.dirlf, text=path).grid(row=idx, sticky=tk.W, column=0, pady=4, padx=4)
            ttk.Checkbutton(self.dirlf,
                variable = var,
                onvalue = 1,
                offvalue = 0,
                command = self.select_path).grid(row=idx, sticky=tk.E, column=1, pady=4, padx=4)
            idx += 1
        
    def add_subdir(self):
        """事件处理函数，添加分类目录"""
        file_path = filedialog.askdirectory(title='打开目录', initialdir=os.path.join(os.path.expanduser("~"), 'Desktop'))
        if not file_path:
            return
        if file_path not in self.sub_dirs.keys():
            self.sub_dirs[file_path] = tk.IntVar(0)
            self.show_sub_dir()
    
    def switch_mode(self, mode='move'):
        """事件处理函数，切换工作模式"""
        self.mode = mode
        self.tip.set("雷那网 - www.tpleina.com |图片: {}/{}|工作模式: {}".format(len(self.images), self.step, self.mode))
        print(self.mode)
    
    def select_path(self):
        """事件处理函数，选中某个分类目录"""
        self.selected_path = [path for path, sts in self.sub_dirs.items() if sts.get() == 1]
        print(self.selected_path)

    def open_imgdir(self):
        """事件处理函数，打开图片目录"""
        file_path = filedialog.askdirectory(title='打开目录', initialdir=os.path.join(os.path.expanduser("~"), 'Desktop'))
        files = map(lambda x: os.path.join(file_path, x), os.listdir(file_path))
        # 获得图片集合
        self.images = [x for x in files if x.split(".")[-1].lower() in self.image_pattern]
        # 更新状态栏
        self.tip.set("雷那网 - www.tpleina.com |图片: {}/0|工作模式: {}".format(len(self.images), self.mode))
        if not self.images:
            self.cv.delete('img')
        self.show_img()
    
    def show_img(self, idx=0):
        """图片显示"""
        if not self.images:
            return
        try:
            self.org_im = Image.open(self.images[idx])
            # 将图片原始信息保存：图片名称，图片路径
            self.org_im.info['image_name'] = os.path.basename(self.images[idx])
            self.org_im.info['image_path'] = self.images[idx]
        except:
            fname = os.path.basename(self.images[idx])
            msgbox.showwarning("告警信息", "{}不是图片格式！".format(fname), icon="error", type="ok")
            return
        s_w, s_h = self.get_screen_size()
        s_h -= 20
        i_w, i_h = self.org_im.size
        rate = max(i_w/s_w, i_h/s_h)
        # rate > 0 图片尺寸大于显示组件尺寸
        # 进行图片缩略
        print(rate)
        if rate > 1:
            self.im = ImageTk.PhotoImage(self.org_im.resize((int(i_w//rate), int(i_h//rate))))
        else:
            self.im = ImageTk.PhotoImage(self.org_im)
        self.cv.delete('img')
        self.cv.create_image((WIN_WIDTH-200)//2, 10, image=self.im, anchor=tk.N, tag="img")

    def get_screen_size(self):
        """获得画板尺寸"""
        self.cv.update()
        return self.cv.winfo_width(), self.cv.winfo_height()
    
    def browse_image(self, direct='up'):
        """事件处理函数，上一个/下一个，图片预览"""
        if not self.images:
            return
        if direct == 'down' and self.step - 1 < 0 :
            msgbox.showwarning("告警信息", "已经是第一张图片了！", icon="error", type="ok")
            return
        self.step = self.step + 1 if 'up' == direct else self.step - 1
        self.step = self.step % len(self.images)
        # 更新状态栏
        self.tip.set("雷那网 - www.tpleina.com |图片: {}/{}|工作模式: {}".format(len(self.images), self.step, self.mode))
        self.show_img(self.step)
    
    def do_image_arrange(self):
        """事件处理函数，实现图片多目录复制/移动"""
        if not self.org_im:
            return
        if not self.selected_path:
            msgbox.showwarning("告警信息", "没有选择分类目录", icon="error", type="ok")
            return 
        if "move" == self.mode:
            # 图片多目录移动
            for path in self.selected_path:
                self.org_im.save(os.path.join(path, self.org_im.info['image_name']))
            else:
                os.remove(self.org_im.info['image_path'])
                self.images.remove(self.org_im.info['image_path'])
                self.tip.set("雷那网 - www.tpleina.com |图片: {}/{}|工作模式: {}".format(len(self.images), self.step, self.mode))
        elif "copy" == self.mode:
            # 图片多目录复制
            for path in self.selected_path:
                self.org_im.save(os.path.join(path, self.org_im.info['image_name']))
        msgbox.showwarning("信息提示", "{} has {}!".format(self.org_im.info['image_name'], self.mode), icon="info", type="ok")
        self.org_im = None


if __name__ == "__main__":
    # 实例化图片分类工具GUI
    mw = tk.Tk()
    mw.title("图片分类工具 - www.tpleina.com")
    mw.iconbitmap('image/logo32.ico')
    mw.geometry("%dx%d+400+100" % (WIN_WIDTH, WIN_HEIGHT))
    ImageGui(mw)
    mw.mainloop()

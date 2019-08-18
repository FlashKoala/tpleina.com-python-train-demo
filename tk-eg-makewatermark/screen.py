# -*- coding:utf-8 -*-
from io import BytesIO
from PIL import Image,ImageGrab,ImageTk
import tkinter as tk
from tkinter import ttk,Canvas
from tkinter import filedialog,messagebox

from conf import CONF
from util import get_desktop_path, gen_dialog_box, is_chinese


class ImageScreen(object):
    """屏幕内容显示类"""
    def __init__(self, mw):
        self.mw = mw
        # 显示图片宽、高
        self.img_w = 0
        self.img_h = 0
        # 右键菜单项
        self.options = ['保存']
        # 状态,是否加载图片
        self.has_img = False
        # 状态,是否显示初始字体
        self.has_initfont = False
        self.init_widgets()

    def init_widgets(self):
        # 创建Labelframe容器
        self.fc = ttk.Frame(self.mw)
        self.fc.pack(fill=tk.BOTH,expand=tk.YES,ipadx=2,ipady=2)
        # 创建右键菜单
        self.right_menu = tk.Menu(self.mw, tearoff = 0)
        for item in self.options:
            # 添加项
            self.right_menu.add_command(label=item, command=self.save_event)
        # 初始Canvas画布
        self.cv = Canvas(self.fc)
        self.cv.pack(fill=tk.BOTH,expand=tk.YES)

    def reset_canvas_size(self):
        """根据图片大小，重置画布尺寸"""
        self.cv.update()
        self.cv['width'], self.cv['height'] = self.img_w, self.img_h
        print('cv size:', self.cv['width'], self.cv['height'])
        self.cv.update()
    
    def add_dashboard(self, board_win):
        """引入操控类实例对象"""
        self.board_win = board_win
        self.img_w, self.img_h = self.board_win.get_win_size()
        self.reset_canvas_size()
        # 添加控制图层，且控制图层在最上面，且控制图层tag: CTL_LAY
        self.cv.create_rectangle(0, 0, self.img_w,self.img_h, width=0, tag=CONF.CTL_LAY)
        # 控制图层绑定右键菜单
        self.cv.tag_bind(CONF.CTL_LAY,'<Button-3>', self.popup)
        # 控制图层绑定双击导入图片
        self.cv.tag_bind(CONF.CTL_LAY,'<Double-1>', self.load_img)
        # 添加初始文字
        self.add_mark("导入图片....", 15, mode="center")
    
    def add_memu(self, memu):
        """引入菜单条类实例对象"""
        self.memu = memu
    
    def reset_ctl_layer(self, tagid):
        """重置控制图层尺寸，并上移控制图层"""
        self.cv.update()
        self.cv.coords(CONF.CTL_LAY, 0, 0, self.cv.winfo_width(), self.cv.winfo_height())
        self.cv.tag_raise(CONF.CTL_LAY, tagid)
        self.cv.update()
    
    def del_canvas(self, tagids):
        """根据tag列表, 删除指定图层"""
        self.cv.delete(*tagids)
        print(self.cv.find_all())

    def popup(self, event):
        """右键菜单事件处理函数"""
        if self.has_img:
            # 有图片执行动作
            self.right_menu.post(event.x_root,event.y_root)
    
    def save_event(self):
        """保存图片事件处理函数"""
        # 保存文件对话框
        filep = filedialog.asksaveasfilename(title='保存图片',
                                        initialdir=get_desktop_path(),
                                        filetypes=CONF.IMAGE_TYPES)
        if filep:
            x, y = self.cv.winfo_rootx(), self.cv.winfo_rooty()
            # 图片区域截屏
            im = ImageGrab.grab((x, y, x+self.img_w, y+self.img_h))
            if not "png" == filep.split(".")[-1].lower().strip():
                filep += ".png"
            # 是否压缩图片
            if self.memu.iscompress():
                out = BytesIO()
                im.save(out,'png')
                out.seek(0)
                self.memu.make_compress_img(out.read(), filep)
            else:
                im.save(filep)
            gen_dialog_box("图片保存成功！")
    
    def show_img(self, imgp):
        """图片显示"""
        if imgp:
            # 校验图片格式
            try:
                im = Image.open(imgp)
                self.cv.im = ImageTk.PhotoImage(im)
            except:
                gen_dialog_box("非图片格式!","Error")
                return
            # 删除上一个水印图片
            self.del_canvas([CONF.IMG_TAG, CONF.MARK_TAG])
            self.img_w, self.img_h = im.size[0], im.size[1]
            # 重置画布尺寸
            self.reset_canvas_size()
            # 绘制图片
            cvid = self.cv.create_image(0, 0, image=self.cv.im, anchor=tk.NW,tag=CONF.IMG_TAG)
            self.has_img = True
            # 调整控制图层
            self.reset_ctl_layer(cvid)
            print('cv size:', self.cv['width'], self.cv['height'])
            cvids = self.cv.find_below(cvid)
            # 删除之前图片、水印
            self.del_canvas(cvids)
            self.cv.update()

    def load_img(self, event):
        """导入图片，并显示图片"""
        imgp = filedialog.askopenfilename(title='导入图片',
                                            filetypes=CONF.IMAGE_TYPES,
                                            initialdir=get_desktop_path())
        if imgp:
            self.show_img(imgp)

    def calc_pos(self, c_w, c_h, position="right-down"):
        """不同水印模式下,绘画起始点坐标"""
        print(position,int(self.cv['width']),int(self.cv['width']) - c_w - CONF.BASE_P2, c_w)
        if "left-up" == position:
            px, py = CONF.BASE_P1, CONF.BASE_P1
        elif "left-down" == position:
            px = CONF.BASE_P1
            py = int(self.cv['height']) - c_h - CONF.BASE_P2
        elif "right-up" == position:
            px = int(self.cv['width']) - c_w
            py = CONF.BASE_P1
        elif "right-down" == position:
            px = int(self.cv['width']) - c_w
            py = int(self.cv['height']) - c_h - CONF.BASE_P2
        elif "center" == position:
            px = int(self.cv['width'])//2 - c_w//2
            py = int(self.cv['height'])//2 - c_h//2
        return px, py

    def calc_x_offset(self, text, size):
        offset = sum([size*1.6 for st in text if is_chinese(st)])
        offset += sum([size*0.8 for st in text if not is_chinese(st)])
        return offset

    def add_mark(self, text, fn_size, clr=None, mode="left-up"):
        """添加水印"""
        print('fn_size',fn_size)
        if "all" == mode and self.has_img:
            self.cv.delete(CONF.MARK_TAG)
            self.add_all_text(text, fn_size, clr)
        elif self.has_img or not self.has_initfont:
            self.cv.delete(CONF.MARK_TAG)
            px, py = self.calc_pos(self.calc_x_offset(text, fn_size), fn_size, mode)
            cvid = self.cv.create_text(px, py,
                        text=text,
                        font=("文泉驿微米黑", fn_size),
                        fill=clr,
                        anchor=tk.NW,
                        tag=CONF.MARK_TAG)
            self.reset_ctl_layer(cvid)
            self.has_initfont = True

    def add_all_text(self, text, fn_size, clr=None):
        """mode=all,水印呈现效果"""
        max_w, max_h = self.img_w, self.img_h
        px, py = CONF.BASE_P1, CONF.BASE_P1
        print(max_w, max_h)
        while(py < max_h):
            while(px < max_w):
                cvid = self.cv.create_text(px, py,
                            text=text,
                            font=("文泉驿微米黑", fn_size),
                            fill=clr,
                            anchor=tk.NW,
                            tag=CONF.MARK_TAG)
                self.reset_ctl_layer(cvid)
                px += len(text)*fn_size//4*3 + CONF.BASE_P2
            py += fn_size + CONF.BASE_P2
            px = CONF.BASE_P1

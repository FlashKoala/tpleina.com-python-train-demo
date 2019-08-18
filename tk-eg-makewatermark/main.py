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

import json
import os

import tkinter as tk
from tkinter import Tk,ttk,Canvas

from conf import CONF
# 导入各组件
from menu import WinMenu, get_apikey, set_apikey
from dashboard import DashBoard
from screen import ImageScreen
from util import resource_path

# 默认工具设置
SETTINGS = {
    "api-key": "",
    "mark-text": CONF.INIT_MARK_TEXT,
    "color": "black",
    "mark-mode": "right-down",
    "fn-size": 14,
    "iscompress": 1,
    "theme": CONF.DEFAULT_THEME
}

class WaterMarkTool(object):
    """水印生成工具Main Class"""
    def __init__(self):
        # 创建临时目录
        if not os.path.exists(CONF.APP_TMP_PATH):
            os.mkdir(CONF.APP_TMP_PATH)
        self.settings_path = os.path.join(CONF.APP_TMP_PATH, CONF.SETTINGS)
        # 加载设置信息
        while(True):
            # 不存在创建
            if not os.path.exists(self.settings_path):
                with open(self.settings_path, 'w') as f:
                    f.write(json.dumps(SETTINGS, indent=2))
                init_conf = SETTINGS
                break
            else:
                try:
                    # 存在加载
                    init_conf = json.loads(open(self.settings_path, "r").read())
                    break
                except:
                    os.remove(self.settings_path)
        self.mw = Tk()
        self.mw.title(CONF.WIN_TITLE)
        # 设置图标
        self.mw.iconbitmap(resource_path('asset/logo.ico'))
        # 设置全局样式
        self.style = ttk.Style(self.mw)
        # 创建窗口菜单
        self.wmenu = WinMenu(self.mw, self.style)
        # 创建显示区
        self.scr = ImageScreen(self.mw)
        # 创建操作区
        self.dboard = DashBoard(self.mw)
        # 赋值工具设置
        self.dboard.set_font_color(init_conf.get("color"))
        self.dboard.set_font_size(init_conf.get("fn-size"))
        self.dboard.set_mark_mode(init_conf.get("mark-mode"))
        self.dboard.set_text(init_conf.get("mark-text"))
        set_apikey(init_conf.get("api-key"))
        self.wmenu.set_iscompress(init_conf.get("iscompress"))
        # 主题设置
        theme = init_conf.get("theme") if init_conf.get("theme") else CONF.DEFAULT_THEME
        self.wmenu.set_theme(theme)
        # 设置窗口初始主题样式
        self.style.theme_use(theme)
        # 固定窗口大小
        self.mw.resizable(False, False)

    def keep_settings(self):
        # 保存设置到磁盘
        global SETTINGS
        SETTINGS = {
            "api-key": get_apikey(),
            "mark-text": self.dboard.get_text(),
            "color": self.dboard.get_font_color(),
            "mark-mode": self.dboard.get_mark_mode(),
            "fn-size": self.dboard.get_font_size(),
            "iscompress": self.wmenu.get_iscompress(),
            "theme": self.wmenu.get_theme()
        }
        with open(self.settings_path, 'w') as f:
            f.write(json.dumps(SETTINGS, indent=2))
        # 最后关闭窗口
        self.mw.destroy()

    def run(self):
        self.scr.add_dashboard(self.dboard)
        self.scr.add_memu(self.wmenu)
        self.dboard.add_screen(self.scr)
        self.wmenu.add_screen(self.scr)
        # 在关闭窗口前，执行设置保存操作
        self.mw.protocol("WM_DELETE_WINDOW", func=self.keep_settings)
        self.mw.mainloop()


if __name__ == "__main__":
    wmt = WaterMarkTool()
    wmt.run()

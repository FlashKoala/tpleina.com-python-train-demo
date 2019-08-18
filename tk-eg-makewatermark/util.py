# -*- coding:utf-8 -*-
import os
import sys

from tkinter import messagebox as msgbox

# 获得桌面路径
get_desktop_path = lambda :os.path.join(os.path.expanduser("~"), 'Desktop')
# 获得windows临时目录
get_os_temppath = lambda :os.path.join(os.path.expanduser("~"), 'AppData/Local')
# 判断字符串是否是中文
is_chinese = lambda x: True if '\u4e00' <= x <= '\u9fa5' else False


def gen_dialog_box(msg, _type="Info"):
    """生产对话框"""
    if "Info" == _type:
        msgbox.showinfo("消息提示", msg, icon="info", type="ok")
    elif "Warning" == _type:
        msgbox.showwarning("告警信息", msg, icon="warning", type="ok")
    elif "Error" == _type:
        msgbox.showwarning("告警信息", msg, icon="error", type="ok")

# 资源文件目录
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
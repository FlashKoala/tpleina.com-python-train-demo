# -*- coding:utf-8 -*-
import os
from util import get_os_temppath

class CONF:
    # 工具软件专属临时目录
    APP_TMP_PATH = os.path.join(get_os_temppath(), "wwwleinacom")
    # 工具标题栏内容
    WIN_TITLE = "雷那网-水印制作工具 - www.tpleina.com"
    # 初始水印文字
    INIT_MARK_TEXT = "雷那网 - www.tpleina.com"
    # 水印模式，5种
    MARK_MODES = [('left-up', '左上'),
                    ('left-down', '左下'), 
                    ('right-up', '右上'),
                    ('right-down', '右下'),
                    ('all', '贯穿')
                    ]
    # 能为以下图片格式添加水印
    IMAGE_TYPES = [("PNG格式", "*.png"), ('JPG格式', '*.jpg')]
    # 最大水印字体长度
    MAX_MARK_LEN = 40
    # 最大水印字体
    MAX_FONT_SIZE = 30
    # 最小水印字体
    MIN_FONT_SIZE = 8
    # 窗口主题样式
    THEMES = [('winnative', 'winnative主题'),
                ('clam', 'clam主题'),
                ('alt', 'alt主题'),
                ('default', 'default主题'),
                ('classic', 'classic主题'),
                ('vista', 'vista主题'),
                ('xpnative', 'xpnative主题')]
    # 窗口默认主题样式
    DEFAULT_THEME = "vista"
    # 偏移量1
    BASE_P1 = 5
    # 偏移量2
    BASE_P2 = 15
    # 控制图层标签
    CTL_LAY = "ctl-layer"
    # 图片图层标签
    IMG_TAG = "IMG"
    # 水印图层标签
    MARK_TAG = 'shuiyin'
    # 设置信息保存文件名
    SETTINGS = 'settings.json'


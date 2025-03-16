#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：logger.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:35 
"""

"""
日志配置模块功能：
1. 统一日志格式
2. 文件与控制台双输出
3. 按模块分日志文件
"""

import logging
import sys
from config.settings import LOG_DIR, LOG_FORMAT, LOG_LEVEL
import os

def get_logger(name):
    """获取模块专用日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # 创建日志目录
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 文件处理器配置
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, f"{name}.log"),
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # 控制台处理器配置
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # 清除已有处理器避免重复
    logger.handlers.clear()
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

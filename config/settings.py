#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：settings.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:25 
"""

import os

# Excel文件配置
EXCEL_PATH = "E:\php\phpstudy\phpstudy_pro\WWW\company\content.xlsx"  # Excel文件绝对路径
EXCEL_HEADERS = ["time", "postName", "desc", "status"]  # Excel必需字段

# 文件路径配置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
LOG_DIR = os.path.join(ROOT_DIR, "logs")  # 日志目录

# ADB配置
ADB_COMMAND = "adb"  # ADB命令路径（假设已加入系统PATH）

# 设备映射配置（逻辑名称 -> 物理设备序列号）
DEVICE_MAPPING = {
    "deviceA": "ABCD1234",  # 示例设备
    "deviceB": "EFGH5678",
    "deviceC": "IJKL9012"
}

# 各设备的文件存储路径
DEVICE_PATHS = {
    "ABCD1234": "/storage/emulated/0/Pictures",  # Android设备图片目录
    "EFGH5678": "/storage/emulated/0/Pictures",
    "IJKL9012": "/storage/emulated/0/Pictures"
}

# 日志配置
LOG_LEVEL = "INFO"  # 日志级别
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日志格式

# 任务状态映射表（中英文对照）
TASK_STATUS = {
    "PENDING": "待执行",
    "PROCESSING": "执行中",
    "SUCCESS": "执行成功",
    "FAILED": "执行失败",
    "DEVICE_NOT_FOUND": "设备未连接",
    "INVALID_PATH": "路径无效"
}

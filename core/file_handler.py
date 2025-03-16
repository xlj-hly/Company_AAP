#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：file_handler.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:26 
"""

"""
文件处理模块功能：
1. 根据设备映射关系传输文件
2. 支持多图片文件传输
3. 处理设备连接状态检查
4. 返回详细的传输状态
"""

import os
from utils.adb_utils import ADBHelper
from utils.logger import get_logger
from config.settings import DEVICE_MAPPING, TASK_STATUS

logger = get_logger(__name__)

class FileHandler:
    def __init__(self, root_dir):
        self.root_dir = root_dir       # 项目根目录
        self.adb_helper = ADBHelper()  # ADB工具实例
    
    def transfer_images(self, post_name, time_str):
        """
        图片传输主方法
        参数：
            post_name: 设备名称（对应设备映射）
            time_str: 时间字符串（用于构建路径）
        返回：
            (成功状态, 状态码)
        """
        try:
            # 设备映射检查
            device_id = DEVICE_MAPPING.get(post_name)
            if not device_id:
                msg = f"未找到设备映射关系: {post_name}"
                logger.error(msg)
                return False, "DEVICE_NOT_FOUND"
            
            # 源路径验证
            source_dir = os.path.join(self.root_dir, post_name, time_str, 'img')
            if not os.path.exists(source_dir):
                msg = f"源目录不存在: {source_dir}"
                logger.error(msg)
                return False, "INVALID_PATH"
            
            # 获取图片文件列表
            images = [f for f in os.listdir(source_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            if not images:
                logger.warning(f"目录中没有图片文件: {source_dir}")
                return False, "INVALID_PATH"
            
            # 批量传输处理
            transfer_results = []
            for img in images:
                source_path = os.path.join(source_dir, img)
                success, status = self.adb_helper.push_file(device_id, source_path)
                transfer_results.append((success, status))
            
            # 传输结果分析
            if all(result[0] for result in transfer_results):
                return True, "SUCCESS"
            elif any(result[0] for result in transfer_results):
                return False, "PARTIAL_SUCCESS"  # 部分成功
            else:
                return False, transfer_results[0][1]  # 返回第一个错误
                
        except Exception as e:
            logger.error(f"文件传输过程出错: {str(e)}")
            return False, "FAILED"

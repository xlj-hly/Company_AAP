#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：adb_utils.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:35 
"""

"""
ADB工具模块功能：
1. 管理ADB设备连接
2. 执行文件传输命令
3. 设备状态实时监控
"""

import subprocess
from utils.logger import get_logger
from config.settings import ADB_COMMAND, DEVICE_PATHS
import re

logger = get_logger(__name__)

class ADBHelper:
    def __init__(self):
        self.connected_devices = set()  # 已连接设备集合
        self.update_connected_devices() # 初始化设备列表
    
    def update_connected_devices(self):
        """更新已连接的设备列表"""
        try:
            result = subprocess.run(
                [ADB_COMMAND, 'devices'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # 解析ADB输出
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            self.connected_devices = {
                line.split()[0] for line in lines 
                if line.strip() and 'device' in line  # 过滤掉未授权设备
            }
            
            logger.info(f"当前连接的设备: {self.connected_devices}")
            return self.connected_devices
            
        except subprocess.CalledProcessError as e:
            logger.error(f"获取设备列表失败: {str(e)}")
            self.connected_devices = set()
            return set()
    
    def is_device_connected(self, device_id):
        """检查指定设备是否在线"""
        self.update_connected_devices()  # 每次检查前更新状态
        return device_id in self.connected_devices
    
    def push_file(self, device_id, source_path):
        """
        ADB文件传输方法
        参数：
            device_id: 设备序列号
            source_path: 本地文件路径
        返回：
            (成功状态, 状态消息)
        """
        try:
            # 设备连接检查
            if not self.is_device_connected(device_id):
                msg = f"设备 {device_id} 未连接"
                logger.warning(msg)
                return False, "DEVICE_NOT_FOUND"
            
            # 目标路径验证
            target_path = DEVICE_PATHS.get(device_id)
            if not target_path:
                msg = f"未找到设备 {device_id} 的目标路径配置"
                logger.error(msg)
                return False, "INVALID_PATH"
            
            # 构建ADB命令
            command = [
                ADB_COMMAND,
                '-s', device_id,  # 指定设备
                'push',
                source_path,
                target_path
            ]
            
            # 执行命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"文件传输成功: {source_path} -> {device_id}")
            return True, "SUCCESS"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"ADB 传输失败: {str(e)}")
            return False, "FAILED"

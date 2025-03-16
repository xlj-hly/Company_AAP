#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：excel_monitor.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:25 
"""

"""
Excel文件监控模块功能：
1. 使用watchdog库进行文件系统监控
2. 定时轮询机制双重保障数据同步
3. 数据变化检测（MD5哈希比对）
4. 线程安全的数据读取
5. 数据缓存机制提升性能
"""

import os
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import get_logger
import threading
import time
from datetime import datetime
import hashlib

logger = get_logger(__name__)

class ExcelEventHandler(FileSystemEventHandler):
    """文件系统事件处理器（观察者模式）"""
    
    def __init__(self, monitor):
        self.monitor = monitor  # 所属监控器实例
        self.last_modified = 0  # 最后修改时间戳
        self.cooldown = 1  # 事件冷却时间（防止重复触发）
        
    def on_modified(self, event):
        """处理文件修改事件"""
        if not event.is_directory and event.src_path.endswith('.xlsx'):
            current_time = time.time()
            # 冷却时间检查避免重复触发
            if current_time - self.last_modified > self.cooldown:
                self.last_modified = current_time
                logger.info(f"检测到Excel文件变化: {event.src_path}")
                # 触发强制检查
                self.monitor.check_excel_data(force_check=True)

class ExcelMonitor:
    """Excel文件监控器（主体）"""
    
    def __init__(self, excel_path, headers):
        self.excel_path = excel_path  # 监控的Excel路径
        self.headers = headers        # 必须包含的字段
        self.observer = Observer()   # 文件系统观察者
        self.last_data_hash = None   # 上次数据哈希值
        self.last_check_time = 0     # 上次检查时间
        self.poll_interval = 60      # 轮询间隔（秒）
        self.force_check_interval = 5 # 强制检查间隔
        self._stop_flag = False      # 停止标志
        self._lock = threading.Lock() # 线程锁
        self._data_cache = None      # 数据缓存
        self._cache_time = 0         # 缓存时间
        self.cache_ttl = 2           # 缓存有效期
    
    def calculate_data_hash(self, df):
        """计算数据帧的MD5哈希值用于变化检测"""
        data_str = df.to_string()
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def read_excel_safe(self):
        """安全读取Excel文件（带重试机制）"""
        max_retries = 3  # 最大重试次数
        retry_delay = 1  # 重试间隔
        
        for attempt in range(max_retries):
            try:
                return pd.read_excel(self.excel_path)
            except (PermissionError, IOError) as e:
                if attempt == max_retries - 1:  # 最后一次尝试仍失败
                    logger.error(f"无法读取Excel文件: {str(e)}")
                    raise
                time.sleep(retry_delay)
    
    def check_excel_data(self, force_check=False):
        """核心数据检查方法"""
        current_time = time.time()
        
        # 缓存有效性检查
        if not force_check and self._data_cache is not None:
            if current_time - self._cache_time < self.cache_ttl:
                return self._data_cache
        
        try:
            with self._lock:  # 线程安全读取
                df = self.read_excel_safe()
                current_hash = self.calculate_data_hash(df)
                
                # 数据验证（过滤空值行）
                valid_rows = df.dropna(subset=self.headers)
                
                # 哈希变化检测
                if force_check or self.last_data_hash != current_hash:
                    logger.info(f"Excel数据更新 - 有效数据行数: {len(valid_rows)}")
                    logger.info(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    self.last_data_hash = current_hash
                    
                    # 更新缓存
                    self._data_cache = valid_rows
                    self._cache_time = current_time
                    
                    return valid_rows
                
                return self._data_cache if self._data_cache is not None else valid_rows
                
        except Exception as e:
            logger.error(f"检查Excel数据时发生错误: {str(e)}")
            return pd.DataFrame()  # 返回空数据帧避免崩溃
    
    def poll_excel(self):
        """轮询线程方法（备用检查机制）"""
        while not self._stop_flag:
            try:
                current_time = time.time()
                # 定期强制检查
                if current_time - self.last_check_time >= self.poll_interval:
                    self.check_excel_data(force_check=True)
                    self.last_check_time = current_time
                time.sleep(self.force_check_interval)
            except Exception as e:
                logger.error(f"轮询检查时发生错误: {str(e)}")
                time.sleep(5)  # 错误时延长等待
    
    def start_monitoring(self):
        """启动监控服务"""
        # 初始化文件系统监控
        event_handler = ExcelEventHandler(self)
        self.observer.schedule(event_handler, path=os.path.dirname(self.excel_path))
        self.observer.start()
        
        # 启动轮询线程
        self.poll_thread = threading.Thread(target=self.poll_excel, daemon=True)
        self.poll_thread.start()
        
        logger.info(f"Excel监控服务已启动 - 文件: {self.excel_path}")
        # 初始数据检查
        self.check_excel_data(force_check=True)
    
    def stop_monitoring(self):
        """停止监控服务"""
        self._stop_flag = True
        self.observer.stop()
        self.observer.join()
        logger.info("Excel监控服务已停止")
    
    def get_valid_rows(self):
        """获取有效数据行（带缓存检查）"""
        return self.check_excel_data()
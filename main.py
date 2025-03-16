#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：main.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:35 
"""

"""
主程序模块功能：
1. 整合各模块功能
2. 信号处理
3. 主循环控制
4. 状态更新管理
"""

from core.excel_monitor import ExcelMonitor
from core.task_scheduler import TaskScheduler
from core.file_handler import FileHandler
from config.settings import *
import pandas as pd
import time
import signal
import sys
from utils.logger import get_logger

logger = get_logger(__name__)

class Application:
    def __init__(self):
        # 初始化核心组件
        self.excel_monitor = ExcelMonitor(EXCEL_PATH, EXCEL_HEADERS)
        self.task_scheduler = TaskScheduler()
        self.file_handler = FileHandler(ROOT_DIR)
        self.running = True  # 运行状态标志
    
    def signal_handler(self, signum, frame):
        """处理系统终止信号"""
        logger.info("收到终止信号，正在关闭服务...")
        self.running = False
        self.excel_monitor.stop_monitoring()
        sys.exit(0)
    
    def update_excel_status(self, row_index, status):
        """更新Excel中的任务状态"""
        try:
            df = pd.read_excel(EXCEL_PATH)
            df.at[row_index, 'status'] = status
            df.to_excel(EXCEL_PATH, index=False)
            logger.info(f"更新任务状态: 行 {row_index + 1}, 状态 {status}")
        except Exception as e:
            logger.error(f"更新Excel状态失败: {str(e)}")
    
    def run(self):
        """运行应用"""
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 启动Excel监控
        self.excel_monitor.start_monitoring()
        
        logger.info("应用程序已启动")
        
        try:
            while self.running:
                # 获取有效数据
                valid_rows = self.excel_monitor.get_valid_rows()
                
                # 处理每一行数据
                for index, row in valid_rows.iterrows():
                    # 如果状态不为空且不是失败状态，跳过
                    current_status = str(row.get('status', '')).strip()
                    if current_status and current_status not in ['FAILED', 'DEVICE_NOT_FOUND']:
                        continue
                    
                    # 处理文件传输任务
                    success, status = self.file_handler.transfer_images(
                        row['postName'],
                        row['time']
                    )
                    
                    # 更新Excel状态
                    self.update_excel_status(index, TASK_STATUS[status])
                    
                    # 如果文件传输成功，添加定时任务
                    if success:
                        self.task_scheduler.add_task(row)
                
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"程序运行异常: {str(e)}")
        finally:
            self.excel_monitor.stop_monitoring()
            logger.info("应用程序已停止")

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main()

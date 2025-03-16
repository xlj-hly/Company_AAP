"""
项目结构说明：

- config/settings.py: 全局配置文件，包含路径、设备映射、日志配置等
- core/excel_monitor.py: Excel 文件监控模块，负责检测文件变化和数据更新
- core/file_handler.py: 文件处理模块，负责设备文件传输
- core/task_scheduler.py: 任务调度模块，管理定时任务
- utils/adb_utils.py: ADB 工具类，封装 ADB 命令操作
- utils/logger.py: 日志配置模块
- main.py: 主程序入口，整合各模块功能

执行流程：

1. 主程序启动 Excel 文件监控（文件系统监控+轮询机制）
2. 监控到 Excel 变化后读取并验证数据
3. 对每个有效任务进行文件传输
4. 更新 Excel 中的任务状态
5. 调度未来时间的任务执行
   """

git remote add origin https://github.com/xlj-hly/Company_AAP.git

git branch -M main

git push -u origin main

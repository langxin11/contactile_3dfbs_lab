# VIS 可视化软件 — 摘要

**文档**: `docs/manuals/3DFBSVIS_B3.0_MAN_DEC24.pdf`  
**版本**: Beta v3.0 (DEC24)

## 概述

Java 桌面 GUI 应用，用于实时可视化 3DFBS 传感器数据。

> 注意：VIS 软件为 Windows 版本，需在 Windows 上运行。Linux 下可通过 Python/C++ SDK 自行开发可视化界面。

## 功能

- 传感器力可视化：俯视 2D 表示，十字线表示 X/Y 偏移，灰色圆表示 Z 压缩
- 实时力-时间曲线图：X=黄色, Y=绿色, Z=蓝色
- 数据记录 (CSV)
- 键盘快捷键操作

## 日志文件

- 位置: `./Logs/LOG_YYMMDD_hhmmss.csv`
- 格式: `T_us, S0_G_FX, S0_G_FY, S0_G_FZ, ..., S4_G_FZ`

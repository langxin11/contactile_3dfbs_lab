# 3DFBSxx 三维力按钮传感器 — 数据手册摘要

**文档**: `docs/manuals/3DFBS_Datasheet_Rev_7.pdf`  
**来源**: Contactile Pty Ltd

## 概述

3DFBS 是一种基于光学原理的三维力测量传感器。内部采用硅胶柱配合光学传感器和数字电路，将物理形变转换为三维力数据。每个传感器出厂前已完成标定。

- 外形尺寸: 14.0 (W) x 19.0 (L) x 8.9 (H) mm
- 安装: 2× M1.6 螺丝 + 8-way 0.5mm pitch FPC 排线
- 外壳: 阳极氧化铝 + 硅橡胶接触面

## 型号与量程

| 型号 | X/Y 量程 (N) | Z 量程 (N) | 分辨率 (N) |
|------|-------------|-----------|-----------|
| 3DFBS04 | ±4 | 0–4 | ±0.005 |
| 3DFBS12 | ±8 | 0–12 | ±0.010 |
| 3DFBS20 | ±12 | 0–20 | ±0.010 |

## 通信接口

| 接口 | 参数 |
|------|------|
| I2C | 默认地址 0x57, 支持时钟拉伸, max 40ms |
| SPI | Mode 0, 最高 3MHz, 需 tCD ≥ 250µs, tDC ≥ 10µs |
| 默认 | 出厂默认为 SPI |

可通过 **Interface Bootstrapping** (拉低 INT 再上电) 或 **Set Comms Mode 命令** 切换接口。

## 工作模式

### Idle 模式
- 上电/复位后的默认模式
- 每次读取需发送命令 + 数据交换，开销较大

### Active 模式
- 连续采集数据，通过 INT 引脚同步
- 配置命令 `Set Active Data` (0x0B) + `Set Active Frequency` (0x09, 最小 25Hz)
- 进入命令 `Enter Active` (0x0D)
- 一旦收到任何命令即自动退回 Idle 模式

## 关键命令

| 命令 | 代码 | 说明 |
|------|------|------|
| NOP | 0x01 | 返回 0xAA，通信测试 |
| Get Status | 0x02 | 读取设备状态 |
| Get Data | 0x03 | 读取 X/Y/Z 力 + 温度 (28 bytes, float32) |
| Bias Sensor | 0x0F | 置零标定（类似天平去皮） |
| Set Active Data | 0x0B | 配置 Active 模式输出的数据类型 |
| Enter Active | 0x0D | 进入 Active 模式 |
| Set I2C Address | 0x10 | 更改 I2C 地址（需复位生效） |
| Set Comms Mode | 0x13 | 切换 I2C/SPI（需复位生效） |
| Who Am I | 0x11 | 读取硬件 ID (32 bytes string) |

> **必须 Bias**: 首次使用或传感器无负载时必须执行 Bias，否则可能返回 NaN 或不正确数据

## 电气参数

| 参数 | 值 |
|------|-----|
| VCC | 2.6–3.6 V (典型 3.3 V) |
| 最大 Z 受压 | 100 N |
| 最大 X/Y 剪切 | 50 N |
| 工作温度 | -40 ~ +105 °C |

## 注意事项

- 禁止拆解、钻孔、攻丝或修改外壳
- 避免在磨蚀性表面或尖锐边缘使用
- 强光可能导致微小读数偏移
- 强电磁场（如 MRI）可能干扰
- 温度变化会引起读数漂移，建议每次在传感器无负载时重新 Bias

## 资源链接

- C3DFBS MCU 库: https://github.com/contactile/c3dfbs

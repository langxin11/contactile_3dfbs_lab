# ROS2 集成使用指南

**文档**: `docs/manuals/3DFBSROS2_B1.0_MAN_DEC24.pdf`  
**版本**: Beta v1.0 (DEC24)

## 概述

ROS2 节点 `buttonsensor_ros2_v1` 基于 C++ Linux SDK 实现，将 DEV001 的传感器数据发布为 ROS2 topic。

- 测试环境: Ubuntu 20.04 + ROS2 Foxy
- 兼容性: 理论可运行在 Humble / Iron / Jazzy 等 modern ROS2 发行版
- 许可证: LGPLv3

## ROS2 Package 结构

源文件位于 Contactile USB 的 `SOFTWARE/ROS2/` 目录下，两个 package：

```
ros2_contactile_sensors/
├── buttonsensor_ros2_v1/        ← 主节点
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── src/
│   │   ├── buttonsensor_ros2_node.cpp
│   │   └── buttonsensor_ros2_node.hpp
│   ├── lib/                     ← 内置 libPTSDK.a + 头文件
│   └── launch/
│       └── buttonsensor.launch.py
└── sensor_interfaces/           ← 自定义消息/服务
    ├── CMakeLists.txt
    ├── package.xml
    ├── msg/
    │   └── ButtonSensorState.msg
    └── srv/
        └── BiasRequest.srv
```

## 安装步骤

```bash
# 1. 复制到 ROS2 workspace
cp -r ros2_contactile_sensors /path/to/ros2_ws/src/

# 2. 编译消息接口
cd /path/to/ros2_ws
colcon build --packages-select sensor_interfaces

# 3. 编译节点
colcon build --packages-select buttonsensor_ros2_v1

# 4. source
source install/setup.bash
```

## 启动节点

```bash
ros2 launch buttonsensor_ros2_v1 buttonsensor.launch.py
```

## 启动参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `hub_id` | int | 0 | DEV001 标识符 |
| `n_sensors` | int | 10 | 传感器数量（必须为 10，兼容旧版） |
| `com_port` | string | `/dev/ttyACM0` | 串口设备路径 |
| `baud_rate` | int | 9600 | 波特率 |
| `parity` | int | 0 | 校验 (0=NONE) |
| `byte_size` | int | 8 | 字节大小 |
| `log_file_rate` | int | 100 | 日志采样率 (100/500/1000 Hz) |

> 波特率用 **9600**（Python SDK 是 115200，注意区别）

## 发布的话题

| Topic | 消息类型 | 说明 |
|-------|---------|------|
| `/hub_0/sensor_0` | ButtonSensorState | PORT 0 传感器数据 |
| `/hub_0/sensor_1` | ButtonSensorState | PORT 1 |
| `/hub_0/sensor_2` | ButtonSensorState | PORT 2 |
| `/hub_0/sensor_3` | ButtonSensorState | PORT 3 |
| `/hub_0/sensor_4` | ButtonSensorState | PORT 4 |
| `/hub_1/sensor_5`–`_9` | ButtonSensorState | 始终为 0（向后兼容） |

### ButtonSensorState.msg

```
int64 tus       # 时间戳 (µs)
float32 gfx     # X 轴力 (N)
float32 gfy     # Y 轴力 (N)
float32 gfz     # Z 轴力 (N)
```

## 服务

| Service | 类型 | 说明 |
|---------|------|------|
| `SendBiasRequest` | BiasRequest.srv | 传感器置零（约 2s） |

Bias 前确保传感器无负载至少 1 秒。

## 查看数据示例

```bash
# 查看话题列表
ros2 topic list

# 查看传感器数据
ros2 topic echo /hub_0/sensor_0

# 调用 Bias 服务
ros2 service call /SendBiasRequest sensor_interfaces/srv/BiasRequest
```

## 日志文件

- 源码中 `listener_` 构造函数的 `bool` 参数控制是否记录日志（需手动修改并重新编译）
- 日志路径: `~/.ros/Logs/LOG_YYYY_MM_DD_hh_mm_ss.csv`
- CSV 格式: 与 Python/C++ SDK 相同

## 注意事项

- 串口权限: 需将用户加入 `dialout` 组: `sudo usermod -aG dialout $USER`
- 即使只接 1 个传感器，`n_sensors` 也必须设为 10
- ROS2 Foxy 是 Ubuntu 20.04 版本，在 Ubuntu 24.04 上建议使用 ROS2 Jazzy 或 Humble，可能需要调整编译

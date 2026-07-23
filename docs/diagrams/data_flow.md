# 数据流图

从传感器物理形变到终端可视化/CSV/ROS2 topic 的完整数据链路。

```mermaid
graph LR
    subgraph Hardware["🔌 硬件层"]
        Sensor["3DFBS 传感器<br/>光学形变 → 数字信号<br/>I2C/SPI, 出厂已标定"]
        FPC["8-way 0.5mm FPC"]
        DEV001["DEV001 (ESP32-S2)<br/>协议转换 + 串口桥接<br/>5× FPC ports, USB-C"]
    end

    subgraph SDK["📦 SDK 层 (vendor/)"]
        Lib["libPTSDK.a<br/>FBS3D_CXX_Pybind wheel"]
        Listener["PTSDKListener<br/>connect / bias / listen"]
        GetForce["PTSDKSensor.getGlobalForce()<br/>→ [Fx, Fy, Fz] N"]
    end

    subgraph App["🖥️ 应用层"]
        direction TB
        Print["contactile_lab.py read<br/>终端打印"]
        CSV["contactile_lab.py record<br/>CSV 归档 (data/)"]
        Live["contactile_lab.py live<br/>DearPyGui 实时力曲线"]
        Replay["contactile_lab.py replay<br/>matplotlib 离线回放"]
        ROS2["ROS2 topic<br/>/hub_0/sensor_0<br/>WrenchStamped"]
    end

    Sensor -->|"I2C/SPI"| FPC --> DEV001
    DEV001 -->|"USB-C UART<br/>/dev/ttyACM0<br/>115200(Py) / 9600(C++/ROS2)"| Lib
    Lib --> Listener --> GetForce
    GetForce --> Print
    GetForce --> CSV
    GetForce --> Live
    GetForce --> Replay
    GetForce --> ROS2

    style Hardware fill:#1a1a2e,stroke:#e94560,color:#eee
    style SDK fill:#1a1a2e,stroke:#f5a623,color:#eee
    style App fill:#1a1a2e,stroke:#0f3460,color:#eee
```

## 关键数据变换

| 阶段 | 数据形式 | 说明 |
|------|---------|------|
| 传感器 | 光学信号 → 数字量 | 硅胶柱形变, 出厂标定矩阵 |
| FPC 总线 | I2C (0x57) / SPI (Mode 0) | DEV001 自动协议适配 |
| USB 串口 | UART 字节流 | CDC ACM, 最高 12Mbit/s |
| libPTSDK | `float[3]` → `[Fx, Fy, Fz]` (N) | C++ struct, pybind 转 Python tuple |
| 应用层 | `(timestamp_us, fx, fy, fz)` | 软件基准扣除 + 降采样 |

## 时间戳链路

```
传感器硬件 ts (us) → PTSDKSensor.getTimestamp_us() → Sample.timestamp_us
主机单调钟 (ns) → time.monotonic_ns()            → Sample.t_monotonic_ns
```

# 三条链路分层架构

C++ / Python / ROS2 三条链路共用同一套 vendor SDK 和硬件，属于并列的三种消费方式。

```mermaid
graph TB
    subgraph CppCol["🟠 C++ 链路 — 最低延迟"]
        direction TB
        C1["cpp_ws/src/minimal_reader.cpp<br/>connect → 可选 bias → readNextSample → CSV/统计"]
        C2["CMake + Make<br/>cpp_ws/src/CMakeLists.txt"]
        C3["libPTSDK.a (静态链接)<br/>vendor/C++LIN/"]
        C4["参数: 9600 baud, pthread"]
        C1 --> C2 --> C3 --> C4
    end

    subgraph PyCol["🔵 Python 链路 — 快速原型"]
        direction TB
        P1["contactile_lab.py (typer CLI)<br/>read | record | live | replay | check"]
        P2["uv + CPython 3.10<br/>dearpygui, matplotlib, typer"]
        P3["FBS3D_CXX_Pybind wheel<br/>cp310-cp310-linux_x86_64.whl"]
        P4["参数: 115200 baud, MAX_SENSOR_SLOTS=10"]
        P1 --> P2 --> P3 --> P4
    end

    subgraph ROS2Col["🟢 ROS2 链路 — 机器人集成"]
        direction TB
        R1["ros2 topic echo /hub_0/sensor_0<br/>ros2 service call /SendBiasRequest"]
        R2["buttonsensor_ros2_v1<br/>colcon build + launch.py"]
        R3["libPTSDK.a (内置)<br/>buttonsensor_ros2_v1/lib/"]
        R4["参数: 9600 baud, geometry_msgs/WrenchStamped"]
        R1 --> R2 --> R3 --> R4
    end

    subgraph HW["⬇️ 共享硬件层"]
        H1["3DFBS Sensor → 8-way 0.5mm FPC → DEV001 (ESP32-S2) → USB-C → /dev/ttyACM0"]
    end

    C4 -.-> HW
    P4 -.-> HW
    R4 -.-> HW

    style CppCol fill:#2d1f0c,stroke:#f5a623,color:#f5a623
    style PyCol fill:#0c2d2d,stroke:#00d4aa,color:#00d4aa
    style ROS2Col fill:#0c1f2d,stroke:#4caf50,color:#4caf50
    style HW fill:#1a1a2e,stroke:#e94560,color:#eee
```

## 链路对比

| | C++ | Python | ROS2 |
|------|-----|--------|------|
| 入口 | `cpp_ws/src/minimal_reader.cpp` | `python_ws/contactile_lab.py` | `ros2 topic echo` |
| 构建 | CMake + Make | uv run | colcon build |
| SDK | `libPTSDK.a` 静态链接 | `cp310` wheel, pybind | `libPTSDK.a` 内置 |
| Python 版本 | — | 3.10 (wheel 约束) | 系统 3.12 |
| 波特率 | 9600 | 115200 | 9600 |
| 依赖 | pthread | dearpygui, matplotlib, typer | rclcpp, geometry_msgs |

## 适用场景

| 场景 | 推荐链路 | 理由 |
|------|---------|------|
| 最低延迟采集 | C++ | 无 GC, 无 GIL, 直接系统调用 |
| 快速原型 + 可视化 | Python | typer CLI, DearPyGui 实时曲线, matplotlib 回放 |
| 机器人系统集成 | ROS2 | 标准 topic/service, RViz 可视化 |
| 数据归档 | Python record | CSV 输出 + 软件基准扣除 |
| 嵌入式部署 | C++ | 静态链接, 无运行时依赖 |

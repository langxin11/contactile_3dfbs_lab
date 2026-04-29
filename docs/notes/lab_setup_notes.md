# Lab 环境搭建笔记

记录在 Ubuntu 24.04 x86_64 上搭建 Contactile 3DFBS 实验环境的实操要点。

## 环境概况

| 项目 | 版本/路径 |
|------|----------|
| OS | Ubuntu 24.04 |
| C++ 编译器 | GCC 13.3.0 |
| CMake | 3.28.3 |
| Python 版本管理 | uv 0.9.5 |
| Python SDK 环境 | CPython 3.10.19 (uv 自动下载) |
| ROS2 | Jazzy |

## Python 版本兼容性

原厂 wheel `fbs3d_cxx_pybind-1.0.2-cp310-cp310-linux_x86_64.whl` 是 CPython 3.10 C 扩展，在 3.12 上直接拒绝安装。

**解决方案**: 用 `uv` 创建 Python 3.10 虚拟环境，uv 自动下载管理任意 CPython 版本，对系统零影响。

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install vendor/PythonLIN/fbs3d_cxx_pybind-1.0.2-cp310-cp310-linux_x86_64.whl
```

## C++ SDK header guard bug

`vendor/C++LIN/PTSDKSensor.h` 的 include guard 有缺陷（`#endif` 在类定义之前），直接 `#include "PTSDKSensor.h"` 会导致 `redefinition of class` 编译错误。

**解决方案**: 只 include `PTSDKListener.h`，它会间接引入 `PTSDKSensor.h`。

```cpp
// ✅ 正确
#include "PTSDKListener.h"

// ❌ 错误：会导致 class 重定义
#include "PTSDKSensor.h"
```

## 波特率差异

C++ SDK（及 ROS2 手册）默认波特率是 **9600**，Python SDK 示例用的是 **115200**。这是原厂 SDK 内部的差异，两边都能正常工作。

```cpp
// C++ / ROS2
int rate = 9600;
```

```python
# Python
rate = 115200
```

## ROS2 Jazzy 兼容性

原厂 ROS2 包在 Foxy (Ubuntu 20.04) 下测试，但在 Jazzy (Ubuntu 24.04) 上：
- 迁移版 `contactile_driver` 已验证通过编译并 mock 模式正常运行
- 使用标准 `geometry_msgs/WrenchStamped` 而非自定义消息
- `colcon build` 时需要指定系统 Python3 路径，避免 uv 环境干扰

```bash
colcon build --packages-select contactile_driver \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
```

## 串口权限

DEV001 连接后在 `/dev/ttyACM0` 出现，需要 dialout 组权限：

```bash
sudo usermod -aG dialout $USER
# 注销重新登录后生效
```

## SDK 对象数要求

即使只连接 1 个传感器，也必须初始化 10 个 `PTSDKSensor` 对象。这是原厂 SDK 为兼容旧版模拟传感器保留的约束。S5~S9 始终返回 0。

## 验证状态 (2026-04-28)

- [x] C++ `minimal_reader` 编译 + 链接通过
- [x] Python `FBS3D_CXX_Pybind` import 通过
- [x] ROS2 `contactile_driver` colcon build 通过
- [x] ROS2 mock 模式启动 + topic echo 验证
- [ ] 真实传感器读取（需硬件）

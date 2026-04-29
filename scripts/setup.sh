#!/bin/bash
# Contactile 3DFBS Lab 一键初始化
# 用法: bash scripts/setup.sh
#
# 包含:
#   - C++ minimal_reader 编译
#   - Python 虚拟环境 + 原厂 wheel 安装
#   - ROS2 驱动编译
#   - 串口权限提示

set -e
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo " Contactile 3DFBS Lab — 环境初始化"
echo "=========================================="
echo ""

# ---- C++ 编译 ----
echo "--- [1/3] 编译 C++ minimal_reader ---"
BUILD_DIR="$LAB_ROOT/cpp_ws/build"
SRC_DIR="$LAB_ROOT/cpp_ws/src"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake "$SRC_DIR"
make -j$(nproc)
echo "  C++ 编译完成"
echo ""

# ---- Python 环境 ----
echo "--- [2/3] 安装 Python 虚拟环境 + 原厂 wheel ---"
PYTHON_WS="$LAB_ROOT/python_ws"
cd "$PYTHON_WS"

if [ ! -d ".venv" ]; then
    uv venv --python 3.10
fi
source .venv/bin/activate
uv pip install "$LAB_ROOT/vendor/PythonLIN/fbs3d_cxx_pybind-1.0.2-cp310-cp310-linux_x86_64.whl"
uv pip install matplotlib pyyaml

# 测试 import
python -c "import FBS3D_CXX_Pybind; print('  FBS3D_CXX_Pybind 导入成功')"
echo "  Python 环境就绪"
echo ""

# ---- ROS2 编译 ----
echo "--- [3/3] 编译 ROS2 驱动 ---"
ROS2_WS="$LAB_ROOT/ros2_ws"
if [ -f /opt/ros/jazzy/setup.bash ]; then
    cd "$ROS2_WS"
    colcon build --packages-select contactile_driver \
        --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3 2>&1 | tail -3
    echo "  ROS2 编译完成"
else
    echo "  跳过: 未找到 ROS2 Jazzy 安装"
fi
echo ""

# ---- 权限提示 ----
echo "=========================================="
echo " 初始化完成！"
echo ""
echo " 环境变量: source $LAB_ROOT/config/env.sh"
echo " C++ 读取: bash $LAB_ROOT/scripts/run_cpp.sh"
echo " Python:   bash $LAB_ROOT/scripts/run_python.sh quick_read"
echo " ROS2 模拟: bash $LAB_ROOT/scripts/run_ros2.sh --mock"
echo " ROS2 真实: bash $LAB_ROOT/scripts/run_ros2.sh --real"
echo ""
echo " 检查硬件: bash $LAB_ROOT/scripts/check_usb.sh"
echo "=========================================="

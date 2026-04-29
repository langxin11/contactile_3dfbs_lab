#!/bin/bash
# 运行 ROS2 Contactile 驱动
# 用法: bash scripts/run_ros2.sh [--real|--mock]

set -e
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROS2_WS="$LAB_ROOT/ros2_ws"

# 需要 source ROS2 环境
if [ ! -f /opt/ros/jazzy/setup.bash ]; then
    echo "未找到 ROS2 Jazzy，请确认安装路径"
    exit 1
fi
source /opt/ros/jazzy/setup.bash
source "$ROS2_WS/install/setup.bash"

MODE="${1:---mock}"

case "$MODE" in
    --real)
        echo "=== 启动真实硬件模式 ==="
        ros2 launch contactile_driver contactile_driver.launch.py mock_mode:=false
        ;;
    --mock)
        echo "=== 启动模拟模式（无硬件测试）==="
        ros2 launch contactile_driver contactile_driver.launch.py mock_mode:=true
        ;;
    *)
        echo "用法: bash scripts/run_ros2.sh [--real|--mock]"
        ;;
esac

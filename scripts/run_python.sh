#!/bin/bash
# 运行 Python 读取脚本
# 用法: bash scripts/run_python.sh [quick_read|stream_csv|live_plot]

set -e
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$LAB_ROOT/python_ws/.venv"
SCRIPT="${1:-quick_read}"

# 激活虚拟环境
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "虚拟环境不存在，请先运行 scripts/setup.sh"
    exit 1
fi
source "$VENV_DIR/bin/activate"

# 加载环境变量
source "$LAB_ROOT/config/env.sh"

# 运行指定脚本
case "$SCRIPT" in
    quick_read)  python "$LAB_ROOT/python_ws/quick_read.py" ;;
    stream_csv)  python "$LAB_ROOT/python_ws/stream_csv.py" ;;
    live_plot)   python "$LAB_ROOT/python_ws/live_plot.py" ;;
    *)           echo "未知脚本: $SCRIPT (可用: quick_read, stream_csv, live_plot)" ;;
esac

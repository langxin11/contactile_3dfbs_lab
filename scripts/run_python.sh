#!/bin/bash
# 运行 Python 读取脚本
# 用法: bash scripts/run_python.sh [quick_read|contactile_lab] [脚本参数...]

set -euo pipefail
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$LAB_ROOT/python_ws/.venv"
SCRIPT="${1:-quick_read}"
if [[ $# -gt 0 ]]; then
    shift
fi

# 激活虚拟环境
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "虚拟环境不存在，请先运行 scripts/setup.sh"
    exit 1
fi
source "$VENV_DIR/bin/activate"

# 加载环境变量
source "$LAB_ROOT/config/env.sh"

case "$SCRIPT" in
    quick_read)      exec python "$LAB_ROOT/python_ws/quick_read.py" "$@" ;;
    contactile_lab)  exec python "$LAB_ROOT/python_ws/contactile_lab.py" "$@" ;;
    *)
        echo "未知脚本: $SCRIPT (可用: quick_read, contactile_lab)" >&2
        exit 2
        ;;
esac

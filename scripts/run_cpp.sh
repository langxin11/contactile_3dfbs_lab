#!/bin/bash
# 编译并运行 C++ 读取/记录示例
# 用法: bash scripts/run_cpp.sh -- --confirm-no-load --duration 2 --output /tmp/cpp_rate.csv

set -euo pipefail
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$LAB_ROOT/cpp_ws/build"
SRC_DIR="$LAB_ROOT/cpp_ws/src"

if [[ "${1:-}" == "--" ]]; then
    shift
fi

echo "=== 编译 C++ minimal_reader ==="
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake "$SRC_DIR"
make -j"$(nproc)"

echo ""
echo "=== 运行 C++ minimal_reader ==="
source "$LAB_ROOT/config/env.sh"
exec "$BUILD_DIR/minimal_reader" "$@"

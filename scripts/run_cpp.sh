#!/bin/bash
# 编译并运行 C++ 最小读取器
# 用法: bash scripts/run_cpp.sh

set -e
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$LAB_ROOT/cpp_ws/build"
SRC_DIR="$LAB_ROOT/cpp_ws/src"

echo "=== 编译 C++ minimal_reader ==="
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake "$SRC_DIR"
make -j$(nproc)

echo ""
echo "=== 运行（按 Ctrl+C 停止）==="
source "$LAB_ROOT/config/env.sh"
exec "$BUILD_DIR/minimal_reader" "$@"

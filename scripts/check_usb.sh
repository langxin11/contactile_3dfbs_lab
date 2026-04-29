#!/bin/bash
# 快速检查 USB/串口状态
# 用法: bash scripts/check_usb.sh

echo "=== USB 串口设备 ==="
ls -l /dev/ttyACM* 2>/dev/null && echo "" || echo "未找到 /dev/ttyACM*"

echo "=== USB 设备列表 (含 Contactile) ==="
lsusb | grep -iE "serial|contactile|esp32|303a" || echo "未检测到已知 Contactile 设备"

echo ""
echo "=== 当前用户串口权限 ==="
if groups | grep -q dialout; then
    echo "  dialout 组: OK"
else
    echo "  dialout 组: 缺失！请运行 sudo usermod -aG dialout $USER 后重新登录"
fi

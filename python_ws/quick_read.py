#!/usr/bin/env python
"""
Contactile 3DFBS 最小读取器 (Python)

用法:
    python quick_read.py
    python quick_read.py --port /dev/ttyACM1 --count 20
"""

import argparse
import os
import sys
import time

import FBS3D_CXX_Pybind as fbs


def main():
    parser = argparse.ArgumentParser(description="Contactile 3DFBS quick reader")
    parser.add_argument("--port", default="/dev/ttyACM0", help="串口设备路径")
    parser.add_argument("--count", type=int, default=10, help="读取次数")
    args = parser.parse_args()

    port = args.port
    rate = 115200
    parity = 0
    byte_size = '\x08'
    log_rate = fbs.PTSDKConstants.LOG_RATE_100

    # 预检查：避免进入 C++ 阻塞调用导致 Ctrl+C 失效
    if not os.path.exists(port):
        print(f"错误: 串口设备不存在: {port}")
        print("提示: 请检查 USB 连接或运行 scripts/check_usb.sh")
        sys.exit(1)

    # 初始化 10 个传感器（兼容原厂接口要求）
    print("初始化传感器对象...")
    sensors = [fbs.PTSDKSensor() for _ in range(10)]

    listener = fbs.PTSDKListener(False)  # 不写 CSV 日志
    for s in sensors:
        listener.addSensor(s)

    # 连接
    print(f"连接串口: {port} @ {rate} baud...")
    res = listener.connect(port, rate, parity, byte_size)
    if res != 0:
        print(f"连接失败！错误码: {res}")
        return

    # 校准
    print("Bias 校准中（请保持传感器无负载）...")
    if listener.sendBiasRequest():
        print("Bias 成功")
    else:
        print("Bias 失败！")
        return

    # 开始监听
    listener.startListening()
    time.sleep(0.5)

    # 读取数据（带异常安全处理）
    print(f"\n读取 {args.count} 次传感器数据 (按 Ctrl+C 可提前终止):")
    print(f"{'#':>4s}  {'FX(N)':>8s}  {'FY(N)':>8s}  {'FZ(N)':>8s}")
    try:
        for i in range(args.count):
            force = sensors[0].getGlobalForce()
            print(f"{i:4d}  {force[0]:8.3f}  {force[1]:8.3f}  {force[2]:8.3f}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        # 无论正常结束还是异常退出，都确保断开连接
        listener.stopListeningAndDisconnect()
        print("已断开")


if __name__ == "__main__":
    main()

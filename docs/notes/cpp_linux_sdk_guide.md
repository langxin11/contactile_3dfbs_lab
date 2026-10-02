# C++ SDK (Linux) 使用指南

**文档**: `docs/manuals/3DFBSC++LIN_B1.0_MAN_DEC24.pdf`  
**版本**: Beta v1.0 (DEC24)

## SDK 文件结构

| 路径 | 文件 | 说明 |
|------|------|------|
| `Include/` | `PTSDK_CPP_LIB.h` | DLL 定义头文件 |
| | `PTSDKConstants.h` | 常量定义 |
| | `PTSDKListener.h` | PTSDKListener 类 |
| | `PTSDKSensor.h` | PTSDKSensor 类 |
| | `PTSDKPillar.h` | PTSDKPillar 类 |
| `Library/` | `libPTSDK.a` | 静态库 |
| `Example/` | `USER_EXAMPLE.cpp` + `Makefile` | 示例与构建文件 |

## 使用步骤

项目内已封装可直接运行的 C++ 记录/测速示例：

```bash
# 查看参数
bash scripts/run_cpp.sh -- --help

# 2 秒 CSV 记录；默认不执行初始硬件去皮
bash scripts/run_cpp.sh -- \
  --duration 2 \
  --output /tmp/cpp_rate.csv

# 如果 DEV001 固件/当前配置使用 115200 baud，可显式覆盖
bash scripts/run_cpp.sh -- \
  --baud-rate 115200 \
  --duration 2 \
  --output /tmp/cpp_rate_115200.csv

# 只统计吞吐，不写 CSV，不逐帧打印
bash scripts/run_cpp.sh -- --duration 2

# 需要初始硬件去皮时显式启用，不需要额外确认参数
bash scripts/run_cpp.sh -- --bias --duration 2
```

CSV 字段与 Python 记录器保持一致：

```text
timestamp_us,t_monotonic_ns,fx,fy,fz,force_norm
```

测速时不要逐帧打印到终端；如需抽样观察，可加 `--print-every 100`。

```cpp
#include "PTSDKConstants.h"
#include "PTSDKListener.h"
#include "PTSDKSensor.h"

// 1. 初始化10个传感器
PTSDKSensor sen0, sen1, ..., sen9;

// 2. 初始化监听器
PTSDKListener listener(true);  // 启用日志

// 3. 添加传感器
listener.addSensor(&sen0);
// ... (10个)

// 4. 连接
char port[] = "/dev/ttyACM0";
int rate = 9600;  // 注意: C++ SDK 默认 9600，Python 版是 115200
int parity = 0;
char byteSize = 8;

// 单线程模式
listener.connect(port, rate, parity, byteSize);
while(true) {
    if(listener.readNextSample()) {
        double force[3];
        sen1.getGlobalForce(force);
        printf("F: %.3f, %.3f, %.3f\n", force[0], force[1], force[2]);
    }
}
listener.disconnect();

// 或 多线程模式
listener.connectAndStartListening(port, rate, parity, byteSize, LOG_RATE_1000);
// ... 主线程做其他事 ...
listener.stopListeningAndDisconnect();

// 5. Bias
listener.sendBiasRequest();
```

## API 总结

### PTSDKListener
| 函数 | 说明 |
|------|------|
| `PTSDKListener(isLog)` | 构造函数 |
| `addSensor(pSensor)` | 添加传感器 |
| `connect(port, rate, parity, byteSize)` | 连接串口 |
| `readNextSample()` | 读取下一个样本（单线程） |
| `connectAndStartListening(port, rate, parity, byteSize, logFileRate)` | 一键连接+多线程监听 |
| `sendBiasRequest()` | 发送 Bias 请求 |
| `stopListeningAndDisconnect()` | 停止并断开 |

### PTSDKSensor
| 函数 | 说明 |
|------|------|
| `getGlobalForce(result[3])` | 获取 XYZ 力 |
| `getTimestamp_us()` | 获取时间戳 (µs) |

## 注意

- C++ 版波特率为 **9600**（非 Python 版的 115200）
- 日志文件与 Python 版格式相同
- 需要链接 `libPTSDK.a`（通过提供的 Makefile 编译）

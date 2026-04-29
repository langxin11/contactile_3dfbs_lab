# Python SDK (Linux) 使用指南

**文档**: `docs/manuals/3DFBSPython_B1.0_MAN_FEB25.pdf`  
**SDK 位置**: `/home/xiaodalaing/contactile/SOFTWARE/PythonLIN/`  
**版本**: Beta v1.0 (FEB25)

## SDK 文件

| 文件 | 说明 |
|------|------|
| `fbs3d_cxx_pybind-1.0.2-cp310-cp310-linux_x86_64.whl` | Python wheel (Python 3.10) |
| `fbs3d_pybind_example.py` | 示例代码 |

## 安装

```bash
pip3 install fbs3d_cxx_pybind-1.0.2-cp310-cp310-linux_x86_64.whl
```

> 注意: wheel 是针对 Python 3.10 编译的，在 Ubuntu 24.04 上可能需要自行创建虚拟环境使用 Python 3.10，或从源码重新编译。

## 导入

```python
import FBS3D_CXX_Pybind
```

## 核心类

### PTSDKConstants
| 常量 | 值 | 说明 |
|------|-----|------|
| X_IND / Y_IND / Z_IND | 0 / 1 / 2 | 维度索引 |
| NDIM | 3 | 空间维度数 |
| LOG_RATE_100 / 500 / 1000 | 100 / 500 / 1000 | 日志采样率 |

### PTSDKSensor
单个传感器的数据访问。

- `__init__()` — 构造函数
- `getGlobalForce()` → `list[float, float, float]` — 获取 XYZ 力
- `getTimestamp_us()` → `int` — 获取时间戳 (µs)

### PTSDKListener
与 DEV001 通信的管理器，管理最多 5 个传感器。

- `__init__(logFlag: bool)` — 构造函数，设置是否记录日志
- `addSensor(pSensor)` — 添加传感器对象
- `connect(port, rate, parity, byteSize)` — 连接串口
- `startListening()` — 启动监听线程（需先 connect）
- `connectAndStartListening(port, rate, parity, byteSize, logFileRate)` — 一键连接+监听
- `sendBiasRequest()` → `bool` — 发送 Bias 请求（约 2s）
- `stopListeningAndDisconnect()` — 停止并断开
- `disconnect()` — 断开串口

## 完整使用流程

```python
import FBS3D_CXX_Pybind

# 1. 初始化10个传感器对象（兼容旧版模拟传感器）
sen = [FBS3D_CXX_Pybind.PTSDKSensor() for _ in range(10)]

# 2. 初始化监听器
listener = FBS3D_CXX_Pybind.PTSDKListener(True)  # 启用日志

# 3. 添加传感器
for s in sen:
    listener.addSensor(s)

# 4. 连接串口
port = "/dev/ttyACM0"
rate = 115200
parity = 0
byteSize = ''
res = listener.connect(port, rate, parity, byteSize)
if res != 0:
    exit("连接失败")

# 5. Bias 置零
listener.sendBiasRequest()

# 6. 开始监听
listener.startListening()

# 7. 读取数据
force = sen[0].getGlobalForce()
print(f"X: {force[0]:.3f}, Y: {force[1]:.3f}, Z: {force[2]:.3f} N")

# 8. 停止并断开
listener.stopListeningAndDisconnect()
```

## 日志文件

- 启用日志时，数据记录在 `./Logs/LOG_YYYY_MM_DD_hh_mm_ss.csv`
- CSV 格式: `T_us, S0_G_FX, S0_G_FY, S0_G_FZ, ..., S9_G_FZ`
- S0–S4 对应 DEV001 的 PORT 0–4
- S5–S9 始终为 0（向后兼容）
- 未连接端口的数值为 0.0

## 注意

- 即使只接 1 个传感器，也必须初始化 10 个 PTSDKSensor 对象
- 在 Ubuntu 24.04 上需要确认 Python 3.10 wheel 兼容性，可能需要重建 wheel
- Bias 时确保传感器无负载至少 1 秒，Bias 过程约 2 秒

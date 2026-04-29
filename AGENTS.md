# AGENTS.md — Contactile 3DFBS Lab

Ubuntu 24.04 x86_64 下 Contactile 3D 力触传感器实验代码库，含 C++ / Python / ROS2 三条链路。

## 1. 项目结构

| 目录 | 说明 |
|------|------|
| `vendor/` | 原厂 SDK，**只读** |
| `cpp_ws/` | C++ 实验区（CMake + Make），入口 `src/minimal_reader.cpp` |
| `python_ws/` | Python 实验区（uv + Python 3.10），入口 `quick_read.py` |
| `ros2_ws/` | ROS2 实验区（colcon），入口 `src/buttonsensor_ros2_v1/` |
| `config/` | YAML 配置文件 |
| `scripts/` | 一键运行脚本（bash） |
| `data/` | 实验数据归档（不入 git） |
| `docs/` | 手册 + 笔记 |

## 2. Vendor 代码规则（只读）

`vendor/` 未经用户明确许可不得修改。如需 workaround：
1. 在 `cpp_ws/` / `python_ws/` / `ros2_ws/` 中写封装/适配层
2. 或在调用处加注释 `// Workaround for vendor bug: ...`

## 3. Python 注释规范

- **语言**：中文
- **内容**：解释 Why，不是 What
- **行内注释**：`#` 前留 2 空格，后留 1 空格
- **模块 docstring**：可执行脚本顶部必须有，含 shebang `#!/usr/bin/env python3`
- **函数 docstring**：public 函数必须有，Google Style，含 Args/Returns/Raises
- **类型注解**：推荐所有函数加（Python 3.10 语法），<50 行脚本可省略
- **常量**：核心逻辑、硬件参数、协议参数中的魔法数字必须提取为常量并注释
- **异常注释**：`try/except/finally` 必须注释捕获原因和资源释放理由
- **物理量**：docstring 中标注单位和坐标系
  - 力: N，力矩: N·m，时间: s，频率: Hz，角度: rad/deg
  - 坐标系: sensor / world / tool / robot_base frame
  - 数组标注 shape，如 `shape=(3,)` 表示 `[fx, fy, fz]`

```python
# ✅ 正确
# C++ pybind 阻塞 I/O 时持有 GIL，导致 Ctrl+C 失效，需预检查设备
if not os.path.exists(port):
    sys.exit(1)

# ❌ 错误：复述代码
# 检查 port 是否存在
```

## 4. 编码风格

- **Python**：ruff/PEP 8，行宽 100，双引号 `"`，导入顺序：标准库 → 第三方 → 本地
- **C++**：与原厂 SDK 保持一致（K&R 大括号），`#pragma once`
- **Bash**：`#!/bin/bash`，`set -euo pipefail`

## 5. 构建与运行

- **Python**：`cd python_ws && uv run python <script.py>`；安装依赖 `uv add <pkg>`
- **C++**：`bash scripts/run_cpp.sh`，不要手动进 build 目录 make
- **ROS2**：`colcon build --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3`

## 6. 硬件安全

- **Bias 校准**：`sendBiasRequest()` 前必须确保传感器**无负载**，否则零点漂移
- **串口释放**：异常退出时必须调用 `stopListeningAndDisconnect()`，否则 `/dev/ttyACM0` 锁死
- **波特率**：C++/ROS2 默认 9600，Python 默认 115200，修改时确保 DEV001 固件一致

## 7. Git 规范

- **不提交**：`data/`、`.venv/`、`build/`、`__pycache__/`
- **提交格式**：`[链路] 描述`，如 `[python] 修复 byte_size 类型错误`

## 8. AI Agent 修改流程

1. 修改前先读相关文件和本 AGENTS.md
2. 先简要说明计划，不大范围改动
3. 只改用户指定的或任务直接相关的最小文件集合
4. 不主动重构无关代码，不格式化整个仓库
5. 不主动执行需硬件连接的命令
6. 不执行 `sudo`、`rm -rf`、`git reset --hard`、`git clean -fd` 等高危命令
7. 修改后说明：改了哪些文件、为什么改、是否改变运行逻辑、建议验证命令

## 9. AI Agent 的 Git 限制

未获用户明确许可，不得执行：`git add`、`git commit`、`git push`、`git reset`、`git rebase`、`git clean`。

生成提交信息时只输出建议 message，不自动提交。不要添加不准确的 `Co-authored-by` trailer。

## 10. Typer CLI 规范

Python CLI 统一使用 Typer，参数用 `typing.Annotated` 写法。

```python
from typing import Annotated
import typer

app = typer.Typer(no_args_is_help=True)

@app.command()
def read(
    port: Annotated[str, typer.Option("--port", "-p")] = "/dev/ttyACM0",
    baud_rate: Annotated[int, typer.Option("--baud-rate", "-b")] = 115200,
    mock: Annotated[bool, typer.Option("--mock")] = False,
) -> None:
    """读取传感器数据。"""
    ...
```

**规则：**
- CLI 只解析参数和错误退出，业务逻辑下沉到普通函数
- `Argument` = 必须给出的主要对象；`Option` = 可选配置
- 串口用 `str`（`Path` 校验会误杀字符设备），内部显式检查存在性
- bias 等危险操作必须显式确认参数（如 `--confirm-no-load`），否则拒绝执行
- 输出：`echo()` 普通信息，`secho(..., err=True)` 错误
- 捕获 `PermissionError`（提示 dialout 组）、`KeyboardInterrupt`（释放串口）
- 测试用 `CliRunner`，默认 `--mock`，不依赖硬件
- 禁止：CLI 写业务逻辑、默认危险操作、交互式 prompt、调用 `sudo`

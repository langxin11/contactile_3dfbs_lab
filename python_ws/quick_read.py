#!/usr/bin/env python3
"""Contactile 3DFBS 最小读取器。

用法:
    uv run python quick_read.py
    uv run python quick_read.py --port /dev/ttyACM1 --count 20
    uv run python quick_read.py --bias
    uv run python quick_read.py --mock
"""

import os
import time
from dataclasses import dataclass
from typing import Annotated, Callable, Optional

import FBS3D_CXX_Pybind as fbs
import typer

DEFAULT_PORT = "/dev/ttyACM0"
DEFAULT_COUNT = 10
BAUD_RATE = 115200
PARITY_NONE = 0
# pybind 接口要求以单字符字符串传递 8-bit byte size，不能直接传整数 8。
BYTE_SIZE_CHAR = "\x08"
# 原厂 SDK 协议固定保留 10 个传感器槽位，即使实验只读取 S0。
MAX_SENSOR_SLOTS = 10
CONNECTION_SETTLE_SEC = 0.5
DISPLAY_INTERVAL_SEC = 0.1

app = typer.Typer(
    name="quick_read",
    help="Contactile 3DFBS 最小读取器",
    no_args_is_help=False,
)


@dataclass(frozen=True)
class ForceSample:
    """单帧 sensor frame 力数据。

    Args:
        fx: X 轴力，单位 N，sensor frame。
        fy: Y 轴力，单位 N，sensor frame。
        fz: Z 轴力，单位 N，sensor frame。
    """

    fx: float
    fy: float
    fz: float


def _emit(progress: Optional[Callable[[str], None]], message: str) -> None:
    if progress is not None:
        progress(message)


def collect_force_samples(
    port: str,
    count: int,
    *,
    bias: bool = False,
    mock: bool = False,
    progress: Optional[Callable[[str], None]] = None,
) -> list[ForceSample]:
    """连接传感器并采集指定数量的力数据。

    默认保留设备当前零点，不执行硬件去皮。真实设备模式下，无论采集成功、
    失败或被中断，都会释放串口。

    Args:
        port: 串口设备路径。
        count: 采样数量。
        bias: 是否在连接后执行一次硬件去皮。
        mock: 是否使用确定性模拟数据，避免访问硬件。
        progress: 可选进度输出回调。

    Returns:
        `ForceSample` 列表，各分量位于 sensor frame，单位 N。

    Raises:
        FileNotFoundError: 串口设备不存在。
        PermissionError: 当前用户无串口访问权限。
        RuntimeError: SDK 连接或硬件去皮失败。
        ValueError: count 小于 1。
        KeyboardInterrupt: 用户中断采集。
    """
    if count < 1:
        raise ValueError("读取次数必须大于 0")

    if bias:
        _emit(progress, "将执行初始硬件去皮")
    else:
        _emit(progress, "未执行初始硬件去皮")

    if mock:
        _emit(progress, "使用模拟数据，不访问传感器")
        return [
            ForceSample(
                fx=index * 0.001,
                fy=-index * 0.001,
                fz=index * 0.002,
            )
            for index in range(count)
        ]

    # pybind 的连接调用可能长时间持有 GIL，先失败可避免进入不可中断的阻塞 I/O。
    if not os.path.exists(port):
        raise FileNotFoundError(port)

    sensors = [fbs.PTSDKSensor() for _ in range(MAX_SENSOR_SLOTS)]
    listener = fbs.PTSDKListener(False)
    for sensor in sensors:
        listener.addSensor(sensor)

    connected = False
    try:
        _emit(progress, f"连接串口: {port} @ {BAUD_RATE} baud...")
        result = listener.connect(port, BAUD_RATE, PARITY_NONE, BYTE_SIZE_CHAR)
        if result != 0:
            raise RuntimeError(f"连接失败，错误码: {result}")
        connected = True

        if bias:
            _emit(progress, "执行初始硬件去皮...")
            if not listener.sendBiasRequest():
                raise RuntimeError("硬件去皮失败")
            _emit(progress, "硬件去皮完成")

        listener.startListening()
        time.sleep(CONNECTION_SETTLE_SEC)

        samples: list[ForceSample] = []
        for _ in range(count):
            force = sensors[0].getGlobalForce()
            samples.append(
                ForceSample(
                    fx=float(force[0]),
                    fy=float(force[1]),
                    fz=float(force[2]),
                )
            )
            time.sleep(DISPLAY_INTERVAL_SEC)
        return samples
    finally:
        # 连接成功后必须统一释放 SDK 线程和串口，避免异常路径锁死字符设备。
        if connected:
            listener.stopListeningAndDisconnect()
            _emit(progress, "已断开")


@app.command()
def read(
    port: Annotated[
        str,
        typer.Option("--port", "-p", help="串口设备路径"),
    ] = DEFAULT_PORT,
    count: Annotated[
        int,
        typer.Option("--count", "-n", help="读取次数", min=1),
    ] = DEFAULT_COUNT,
    bias: Annotated[
        bool,
        typer.Option("--bias", help="连接后执行一次硬件去皮；默认不执行"),
    ] = False,
    mock: Annotated[
        bool,
        typer.Option("--mock", help="使用模拟数据，不访问硬件"),
    ] = False,
) -> None:
    """读取 S0 的三轴力数据。

    Args:
        port: 串口设备路径。
        count: 读取样本数。
        bias: 是否在连接后执行硬件去皮。
        mock: 是否使用模拟数据。

    Returns:
        无。
    """
    # 将业务层异常转换为稳定的 CLI 退出码，同时保留 collect_force_samples 的可复用性。
    try:
        samples = collect_force_samples(
            port,
            count,
            bias=bias,
            mock=mock,
            progress=typer.echo,
        )
    except FileNotFoundError:
        typer.secho(f"错误: 串口设备不存在: {port}", err=True)
        typer.secho("提示: 请检查 USB 连接或运行 scripts/check_usb.sh", err=True)
        raise typer.Exit(code=1) from None
    except PermissionError:
        typer.secho(
            "错误: 无串口访问权限，请确认当前用户属于 dialout 组并重新登录",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except RuntimeError as exc:
        typer.secho(f"错误: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except KeyboardInterrupt:
        typer.echo("用户中断")
        raise typer.Exit(code=130) from None

    typer.echo(f"\n读取 {len(samples)} 次传感器数据:")
    typer.echo(f"{'#':>4s}  {'FX(N)':>8s}  {'FY(N)':>8s}  {'FZ(N)':>8s}")
    for index, sample in enumerate(samples):
        typer.echo(
            f"{index:4d}  {sample.fx:8.3f}  {sample.fy:8.3f}  {sample.fz:8.3f}"
        )


if __name__ == "__main__":
    app()

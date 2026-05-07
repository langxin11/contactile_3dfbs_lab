#!/usr/bin/env python3
"""
Contactile 3DFBS lab CLI — 统一的传感器采集、记录、实时预览和回放工具。

用法:
    # 快速读取（单传感器，含 software baseline）
    uv run python contactile_lab.py read --confirm-no-load --count 20

    # 记录到 CSV
    uv run python contactile_lab.py record --confirm-no-load --duration 10

    # 双传感器实时力曲线
    uv run python contactile_lab.py live --confirm-no-load --sensors 0,1

    # 离线回放
    uv run python contactile_lab.py replay data/run.csv

    # 跳过 software baseline，仅用 SDK bias 对比
    uv run python contactile_lab.py check --confirm-no-load --no-software-baseline

默认先执行 SDK bias，再采样 2 秒软件基准；若任一轴标准差超过 0.02 N，
会认为基准期间存在触碰或扰动并停止运行。CSV 默认保存校正后的力数据。
--rate 是 CLI 目标输出频率；SDK 实际更新更快时会按 timestamp 软件降采样。
"""

import csv
import math
import os
import statistics
import sys
import threading
import time
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Iterable, Iterator, Optional

import FBS3D_CXX_Pybind as fbs
import typer

# ── 常量 ───────────────────────────────────────────────────────────

# Python SDK 链路默认波特率
BAUD_RATE = 115200
PARITY_NONE = 0
# ASCII 退格符 (0x08)，pybind 绑定层要求 str 类型传入
BYTE_SIZE_CHAR = "\x08"
# 原厂 SDK 要求初始化 10 个传感器占位，即使只连接 1 个
MAX_SENSOR_SLOTS = 10
DEFAULT_PORT = "/dev/ttyACM0"
DEFAULT_RATE_HZ = 1000
DEFAULT_SENSOR = 0
DEFAULT_WINDOW_SEC = 4.0
DEFAULT_VIEWPORT_WIDTH = 1600
DEFAULT_VIEWPORT_HEIGHT = 1200
DEFAULT_FORCE_LIMIT_N = 1.0
# 软件基准默认窗口；1000 Hz 下约 2000 点，兼顾启动速度和均值稳定性
DEFAULT_BASELINE_DURATION_SEC = 2.0
# 任一力轴标准差超过该阈值，视为基准期间存在触碰或环境扰动
DEFAULT_BASELINE_STD_LIMIT_N = 0.02
# 低于该样本数时均值不可信，通常表示传感器未出数或索引错误
MIN_BASELINE_SAMPLES = 20
# Dear PyGui 全局字体大小，默认约 13px，增大到 22px 改善高分辨率屏幕可读性
DPG_FONT_SIZE = 22
DPG_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CSV_FIELDS = ("timestamp_us", "t_monotonic_ns", "fx", "fy", "fz", "force_norm")

app = typer.Typer(
    name="contactile_lab",
    help="Contactile 3DFBS 传感器实验工具",
    no_args_is_help=True,
)

# ── 数据模型 ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class Sample:
    """单帧力传感器采样数据。

    所有力分量位于 sensor frame，单位为 N。
    时间戳单位为 us，主机单调时钟单位为 ns。

    Args (字段):
        timestamp_us: 传感器硬件时间戳，单位 us。
        t_monotonic_ns: 主机单调时间戳，单位 ns。
        fx: X 方向力，单位 N。
        fy: Y 方向力，单位 N。
        fz: Z 方向力，单位 N。
    """

    timestamp_us: int
    t_monotonic_ns: int
    fx: float
    fy: float
    fz: float

    @property
    def force_norm(self) -> float:
        return math.sqrt(self.fx * self.fx + self.fy * self.fy + self.fz * self.fz)

    @property
    def row(self) -> dict[str, float | int]:
        return {
            "timestamp_us": self.timestamp_us,
            "t_monotonic_ns": self.t_monotonic_ns,
            "fx": self.fx,
            "fy": self.fy,
            "fz": self.fz,
            "force_norm": self.force_norm,
        }


@dataclass(frozen=True)
class MultiSample:
    """同一时刻多个传感器的采样快照。

    Args (字段):
        timestamp_us: 基准时间戳，单位 us。
        t_monotonic_ns: 主机单调时间戳，单位 ns。
        samples: 传感器索引到 Sample 的映射。
    """

    timestamp_us: int
    t_monotonic_ns: int
    samples: dict[int, Sample]


@dataclass(frozen=True)
class ForceOffset:
    """单个传感器的软件基准 offset。

    Args (字段):
        fx: X 方向力 offset，单位 N，sensor frame。
        fy: Y 方向力 offset，单位 N，sensor frame。
        fz: Z 方向力 offset，单位 N，sensor frame。
    """

    fx: float
    fy: float
    fz: float


@dataclass(frozen=True)
class BaselineStats:
    """软件基准统计结果。

    Args (字段):
        offset: 基准窗口内的平均力，单位 N。
        std: 基准窗口内的标准差，单位 N。
        count: 参与统计的新样本数量。
    """

    offset: ForceOffset
    std: ForceOffset
    count: int


# ── 工具函数 ──────────────────────────────────────────────────────


def _log_rate_constant(rate_hz: int) -> int:
    """将 Hz 值映射为 SDK LOG_RATE 常量。"""
    mapping = {
        100: fbs.PTSDKConstants.LOG_RATE_100,
        500: fbs.PTSDKConstants.LOG_RATE_500,
        1000: fbs.PTSDKConstants.LOG_RATE_1000,
    }
    try:
        return mapping[rate_hz]
    except KeyError as exc:
        raise ValueError(f"不支持的采集频率: {rate_hz}，可选 100, 500, 1000") from exc


def _check_port(port: str) -> None:
    """预检查串口设备是否存在，避免 SDK 阻塞 I/O 时 Ctrl+C 无法中断。"""
    if not os.path.exists(port):
        raise FileNotFoundError(
            f"串口设备不存在: {port}\n"
            "提示: 检查 USB 连接，或运行 scripts/check_usb.sh"
        )


def _parse_sensor_list(value: str) -> list[int]:
    """解析逗号分隔的传感器索引字符串。

    Args:
        value: 逗号分隔的传感器索引，如 "0,1"。

    Returns:
        去重后的传感器索引列表。

    Raises:
        typer.BadParameter: 格式错误或索引越界时抛出。
    """
    sensors: list[int] = []
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        try:
            sensor = int(token)
        except ValueError as exc:
            raise typer.BadParameter("传感器列表格式应类似 0,1") from exc
        if not 0 <= sensor < MAX_SENSOR_SLOTS:
            raise typer.BadParameter(f"传感器索引必须在 0..{MAX_SENSOR_SLOTS - 1} 之间")
        if sensor not in sensors:
            sensors.append(sensor)
    if not sensors:
        raise typer.BadParameter("至少指定一个传感器")
    return sensors


# ── 传感器会话 ────────────────────────────────────────────────────


class SensorSession:
    """管理传感器连接的上下文管理器，确保异常时释放串口。

    进入上下文时自动连接串口、执行 bias 校准（如果 bias=True），
    并可计算软件基准。
    退出上下文时自动调用 stopListeningAndDisconnect() 释放串口。

    Args:
        port: 串口设备路径，如 "/dev/ttyACM0"。
        rate_hz: 目标采集频率，可选 100/500/1000 Hz。
        sensor_index: 主传感器索引，范围 0..MAX_SENSOR_SLOTS-1。
        bias: 是否在连接后执行 bias 校准。
        software_baseline: 是否启用运行时软件基准扣除。
        baseline_duration_sec: 软件基准采样时长，单位 s。
        baseline_std_limit_n: 软件基准扰动检测阈值，单位 N。
        baseline_sensor_indices: 需要建立软件基准的传感器索引列表。
    """

    def __init__(
        self,
        port: str,
        rate_hz: int,
        sensor_index: int = DEFAULT_SENSOR,
        *,
        bias: bool = True,
        software_baseline: bool = True,
        baseline_duration_sec: float = DEFAULT_BASELINE_DURATION_SEC,
        baseline_std_limit_n: float = DEFAULT_BASELINE_STD_LIMIT_N,
        baseline_sensor_indices: Optional[list[int]] = None,
    ) -> None:
        if not 0 <= sensor_index < MAX_SENSOR_SLOTS:
            raise ValueError(f"传感器索引必须在 0..{MAX_SENSOR_SLOTS - 1} 之间")
        self.port = port
        self.rate_hz = rate_hz
        self.sensor_index = sensor_index
        self.bias = bias
        self.software_baseline = software_baseline
        self.baseline_duration_sec = baseline_duration_sec
        self.baseline_std_limit_n = baseline_std_limit_n
        self.baseline_sensor_indices = baseline_sensor_indices or [sensor_index]
        for baseline_sensor_index in self.baseline_sensor_indices:
            if not 0 <= baseline_sensor_index < MAX_SENSOR_SLOTS:
                raise ValueError(f"传感器索引必须在 0..{MAX_SENSOR_SLOTS - 1} 之间")
        self.listener: Optional[fbs.PTSDKListener] = None
        self.sensors: list[fbs.PTSDKSensor] = []
        self._last_timestamp_us: Optional[int] = None
        self._force_offsets: dict[int, ForceOffset] = {}

    def __enter__(self) -> "SensorSession":
        _check_port(self.port)
        log_rate = _log_rate_constant(self.rate_hz)
        self.sensors = [fbs.PTSDKSensor() for _ in range(MAX_SENSOR_SLOTS)]
        self.listener = fbs.PTSDKListener(False)
        for sensor in self.sensors:
            self.listener.addSensor(sensor)

        try:
            typer.echo(
                f"连接串口: {self.port} @ {BAUD_RATE} baud, 目标 {self.rate_hz} Hz..."
            )
            result = self.listener.connectAndStartListening(
                self.port,
                BAUD_RATE,
                PARITY_NONE,
                BYTE_SIZE_CHAR,
                log_rate,
            )
            if result != 0:
                raise RuntimeError(f"连接失败，错误码: {result}")

            time.sleep(0.5)  # 等待稳定连接
            if self.bias:
                typer.echo("Bias 校准中（请保持传感器无负载）...")
                if not self.listener.sendBiasRequest():
                    raise RuntimeError("Bias 失败")
                typer.echo("Bias 成功")
            if self.software_baseline:
                self._compute_software_baseline(self.baseline_sensor_indices)
        except BaseException:
            self.close()
            raise
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self.listener is not None:
            self.listener.stopListeningAndDisconnect()
            self.listener = None
            typer.echo("已断开")

    def read_current(self) -> Sample:
        return self.read_sensor(self.sensor_index)

    def _read_raw(self, sensor_index: int) -> Sample:
        sensor = self.sensors[sensor_index]
        force = sensor.getGlobalForce()
        timestamp_us = int(sensor.getTimestamp_us())
        return Sample(
            timestamp_us=timestamp_us,
            t_monotonic_ns=time.monotonic_ns(),
            fx=float(force[0]),
            fy=float(force[1]),
            fz=float(force[2]),
        )

    def read_sensor(self, sensor_index: int) -> Sample:
        raw = self._read_raw(sensor_index)
        offset = self._force_offsets.get(sensor_index, ForceOffset(0.0, 0.0, 0.0))
        return Sample(
            timestamp_us=raw.timestamp_us,
            t_monotonic_ns=raw.t_monotonic_ns,
            fx=raw.fx - offset.fx,
            fy=raw.fy - offset.fy,
            fz=raw.fz - offset.fz,
        )

    def _should_accept_timestamp(
        self,
        timestamp_us: int,
        last_timestamp_us: Optional[int],
    ) -> bool:
        """按目标输出频率筛选 timestamp，避免 SDK 后台线程过快更新数据。"""
        if timestamp_us == 0:
            return False
        if last_timestamp_us is None:
            return True
        target_interval_us = int(1_000_000 / self.rate_hz)
        return timestamp_us - last_timestamp_us >= target_interval_us

    def _compute_software_baseline(self, sensor_indices: list[int]) -> None:
        """采集无负载窗口并计算运行时 offset，标准差过大时拒绝继续。"""
        if self.baseline_duration_sec <= 0:
            return
        typer.echo(
            "软件基准采样中（请保持传感器无负载）: "
            f"{self.baseline_duration_sec:.1f}s, std limit={self.baseline_std_limit_n:.3f} N"
        )
        values: dict[int, list[Sample]] = {
            sensor_index: [] for sensor_index in sensor_indices
        }
        last_timestamp_us: dict[int, int] = {}
        deadline = time.monotonic() + self.baseline_duration_sec
        sleep_sec = max(0.0002, min(0.002, 0.5 / self.rate_hz))
        while time.monotonic() < deadline:
            for sensor_index in sensor_indices:
                sample = self._read_raw(sensor_index)
                last_timestamp = last_timestamp_us.get(sensor_index)
                if not self._should_accept_timestamp(sample.timestamp_us, last_timestamp):
                    continue
                last_timestamp_us[sensor_index] = sample.timestamp_us
                values[sensor_index].append(sample)
            time.sleep(sleep_sec)

        for sensor_index, samples in values.items():
            if len(samples) < MIN_BASELINE_SAMPLES:
                raise RuntimeError(
                    f"S{sensor_index} 软件基准样本不足: "
                    f"{len(samples)} < {MIN_BASELINE_SAMPLES}"
                )
            fx_values = [sample.fx for sample in samples]
            fy_values = [sample.fy for sample in samples]
            fz_values = [sample.fz for sample in samples]
            stats = BaselineStats(
                offset=ForceOffset(
                    fx=statistics.fmean(fx_values),
                    fy=statistics.fmean(fy_values),
                    fz=statistics.fmean(fz_values),
                ),
                std=ForceOffset(
                    fx=statistics.pstdev(fx_values),
                    fy=statistics.pstdev(fy_values),
                    fz=statistics.pstdev(fz_values),
                ),
                count=len(samples),
            )
            max_std = max(stats.std.fx, stats.std.fy, stats.std.fz)
            if max_std > self.baseline_std_limit_n:
                raise RuntimeError(
                    f"S{sensor_index} 软件基准扰动过大: "
                    f"std Fx/Fy/Fz={stats.std.fx:.5f}/{stats.std.fy:.5f}/{stats.std.fz:.5f} N, "
                    f"limit={self.baseline_std_limit_n:.5f} N"
                )
            self._force_offsets[sensor_index] = stats.offset
            typer.echo(
                f"S{sensor_index} 软件基准: "
                f"offset Fx/Fy/Fz="
                f"{stats.offset.fx:.5f}/{stats.offset.fy:.5f}/{stats.offset.fz:.5f} N, "
                f"std={stats.std.fx:.5f}/{stats.std.fy:.5f}/{stats.std.fz:.5f} N, "
                f"samples={stats.count}"
            )

    def next_sample(self, timeout_sec: float = 2.0) -> Sample:
        """等待并返回下一帧新样本。

        通过对比 timestamp_us 判断是否为新样本，避免重复读取同一帧。

        Args:
            timeout_sec: 超时时间，单位 s。

        Returns:
            下一帧新样本，力分量单位为 N。

        Raises:
            TimeoutError: 超时时间内未收到新样本时抛出。
        """
        deadline = time.monotonic() + timeout_sec
        # 动态 sleep，避免忙等 CPU 空转
        sleep_sec = max(0.0002, min(0.002, 0.5 / self.rate_hz))
        while True:
            sample = self.read_current()
            if self._should_accept_timestamp(sample.timestamp_us, self._last_timestamp_us):
                self._last_timestamp_us = sample.timestamp_us
                return sample
            if time.monotonic() > deadline:
                raise TimeoutError("等待新样本超时")
            time.sleep(sleep_sec)

    def next_multi_sample(
        self,
        sensor_indices: list[int],
        timeout_sec: float = 2.0,
    ) -> MultiSample:
        """等待下一帧新样本，并读取多个传感器的同步数据。

        以 sensor_index 为主传感器等待新帧，其他传感器在同一时刻采样。

        Args:
            sensor_indices: 需要读取的传感器索引列表。
            timeout_sec: 超时时间，单位 s。

        Returns:
            多传感器同步采样快照。

        Raises:
            TimeoutError: 主传感器超时未收到新样本时抛出。
        """
        base_sample = self.next_sample(timeout_sec=timeout_sec)
        samples = {self.sensor_index: base_sample}
        for sensor_index in sensor_indices:
            if sensor_index == self.sensor_index:
                continue
            samples[sensor_index] = self.read_sensor(sensor_index)
        return MultiSample(
            timestamp_us=base_sample.timestamp_us,
            t_monotonic_ns=base_sample.t_monotonic_ns,
            samples=samples,
        )


# ── CSV 工具 ──────────────────────────────────────────────────────


@contextmanager
def csv_writer(path: Optional[str]) -> Iterator[Optional[csv.DictWriter]]:
    """CSV 文件写入上下文管理器。

    自动创建父目录并写入表头。

    Args:
        path: CSV 文件路径。为 None 时 yield None（不写入）。

    Yields:
        csv.DictWriter 实例，或 None。
    """
    if not path:
        yield None
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        yield writer


# ── 终端打印 ──────────────────────────────────────────────────────


def _print_header() -> None:
    """打印终端表格表头。"""
    typer.echo(
        f"{'#':>6s}  {'T(us)':>12s}  {'FX(N)':>9s}  "
        f"{'FY(N)':>9s}  {'FZ(N)':>9s}  {'|F|(N)':>9s}"
    )


def _print_sample(index: int, sample: Sample) -> None:
    """打印单条样本数据到终端。

    Args:
        index: 样本序号。
        sample: 采样数据，力分量单位为 N。
    """
    typer.echo(
        f"{index:6d}  {sample.timestamp_us:12d}  "
        f"{sample.fx:9.3f}  {sample.fy:9.3f}  {sample.fz:9.3f}  "
        f"{sample.force_norm:9.3f}"
    )


# ── 采集与统计 ────────────────────────────────────────────────────


def _collect_samples(
    session: SensorSession,
    *,
    count: Optional[int] = None,
    duration: Optional[float] = None,
    writer: Optional[csv.DictWriter] = None,
    echo: bool = False,
) -> list[Sample]:
    """循环采集传感器样本。

    按 count 或 duration 任一条件满足时停止。

    Args:
        session: 已连接的传感器会话。
        count: 采集样本数，为 None 时不限制。
        duration: 采集时长，单位 s，为 None 时不限制。
        writer: CSV 写入器，为 None 时不写入文件。
        echo: 是否实时打印到终端。

    Returns:
        采集的样本列表，每个样本力分量单位为 N。
    """
    samples: list[Sample] = []
    start = time.monotonic()
    if echo:
        _print_header()
    index = 0
    while True:
        if count is not None and index >= count:
            break
        if duration is not None and time.monotonic() - start >= duration:
            break
        sample = session.next_sample()
        if writer:
            writer.writerow(sample.row)
        if echo:
            _print_sample(index, sample)
        samples.append(sample)
        index += 1
    return samples


def _summarize(samples: list[Sample], label: str = "Summary") -> None:
    """打印样本统计：实际频率、力的均值/最大值、采样间隔分布。"""
    if not samples:
        typer.echo(f"{label}: no samples")
        return
    intervals = [
        (samples[i].timestamp_us - samples[i - 1].timestamp_us) / 1000.0
        for i in range(1, len(samples))
        if samples[i].timestamp_us > samples[i - 1].timestamp_us
    ]
    elapsed_sec = max(
        (samples[-1].timestamp_us - samples[0].timestamp_us) / 1_000_000.0, 0.0
    )
    measured_hz = (
        (len(samples) - 1) / elapsed_sec if elapsed_sec > 0 and len(samples) > 1 else 0.0
    )
    norms = [s.force_norm for s in samples]
    typer.echo(f"\n{label}:")
    typer.echo(f"  samples: {len(samples)}")
    typer.echo(f"  measured rate: {measured_hz:.1f} Hz")
    typer.echo(
        f"  force norm mean/max: {statistics.fmean(norms):.4f} / {max(norms):.4f} N"
    )
    if intervals:
        typer.echo(
            "  interval ms mean/min/max/stdev: "
            f"{statistics.fmean(intervals):.3f} / {min(intervals):.3f} / "
            f"{max(intervals):.3f} / {statistics.pstdev(intervals):.3f}"
        )


def _load_csv(path: str) -> list[Sample]:
    """从 CSV 文件加载样本数据。

    Args:
        path: CSV 文件路径。

    Returns:
        样本列表，每个样本力分量单位为 N。

    Raises:
        ValueError: CSV 缺少必要字段时抛出。
    """
    samples: list[Sample] = []
    with Path(path).open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = set(CSV_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV 缺少字段: {', '.join(sorted(missing))}")
        for row in reader:
            samples.append(
                Sample(
                    timestamp_us=int(float(row["timestamp_us"])),
                    t_monotonic_ns=int(float(row["t_monotonic_ns"])),
                    fx=float(row["fx"]),
                    fy=float(row["fy"]),
                    fz=float(row["fz"]),
                )
            )
    return samples


# ── 实时预览状态 ──────────────────────────────────────────────────


class LiveState:
    """采集线程与 GUI 线程之间的线程安全共享缓冲区。

    使用 deque 实现固定长度的滑动窗口，避免内存无限增长。
    """

    def __init__(self, max_samples: int) -> None:
        self.samples: deque[MultiSample] = deque(maxlen=max_samples)
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.error: Optional[BaseException] = None
        self.count = 0

    def append(self, sample: MultiSample) -> None:
        with self.lock:
            self.samples.append(sample)
            self.count += 1

    def snapshot(self) -> list[MultiSample]:
        with self.lock:
            return list(self.samples)


def _acquisition_worker(
    port: str,
    rate: int,
    sensors: list[int],
    output: Optional[str],
    software_baseline: bool,
    baseline_duration_sec: float,
    baseline_std_limit_n: float,
    state: LiveState,
) -> None:
    """在独立线程中采集传感器数据，写入共享缓冲区。

    与 GUI 主线程解耦，避免 C++ SDK 的阻塞 I/O 卡住界面刷新。

    Args:
        port: 串口设备路径。
        rate: 采集频率，单位 Hz。
        sensors: 需要读取的传感器索引列表。
        output: 可选 CSV 输出路径。
        software_baseline: 是否启用运行时软件基准扣除。
        baseline_duration_sec: 软件基准采样时长，单位 s。
        baseline_std_limit_n: 软件基准扰动检测阈值，单位 N。
        state: 线程安全共享状态对象。
    """
    try:
        with SensorSession(
            port,
            rate,
            sensors[0],
            bias=True,
            software_baseline=software_baseline,
            baseline_duration_sec=baseline_duration_sec,
            baseline_std_limit_n=baseline_std_limit_n,
            baseline_sensor_indices=sensors,
        ) as session:
            with csv_writer(output) as writer:
                while not state.stop.is_set():
                    multi_sample = session.next_multi_sample(sensors)
                    if writer and len(sensors) == 1:
                        writer.writerow(multi_sample.samples[sensors[0]].row)
                    state.append(multi_sample)
    except BaseException as exc:
        state.error = exc
        state.stop.set()


# ── CLI 命令 ──────────────────────────────────────────────────────


@app.command()
def read(
    port: Annotated[
        str,
        typer.Option("--port", "-p", help="串口设备路径"),
    ] = DEFAULT_PORT,
    rate: Annotated[
        int,
        typer.Option("--rate", "-r", help="采集频率 (100/500/1000 Hz)"),
    ] = DEFAULT_RATE_HZ,
    sensor: Annotated[
        int,
        typer.Option("--sensor", "-s", help="传感器索引 (0-9)", min=0, max=9),
    ] = DEFAULT_SENSOR,
    confirm_no_load: Annotated[
        bool,
        typer.Option(
            "--confirm-no-load",
            help="确认传感器无负载，允许执行 bias 校准",
        ),
    ] = False,
    software_baseline: Annotated[
        bool,
        typer.Option(
            "--software-baseline/--no-software-baseline",
            help="SDK bias 后采样无负载均值并在运行时扣除",
        ),
    ] = True,
    baseline_duration_sec: Annotated[
        float,
        typer.Option("--baseline-duration", help="软件基准采样时长 (秒)", min=0.1),
    ] = DEFAULT_BASELINE_DURATION_SEC,
    baseline_std_limit_n: Annotated[
        float,
        typer.Option(
            "--baseline-std-limit",
            help="软件基准扰动标准差阈值 (N)",
            min=0.001,
        ),
    ] = DEFAULT_BASELINE_STD_LIMIT_N,
    count: Annotated[
        int,
        typer.Option("--count", "-n", help="读取样本数", min=1),
    ] = 10,
) -> None:
    """快速终端读取传感器数据。

    默认读取 10 帧并打印到终端。
    需要 --confirm-no-load 确认无负载后才执行 bias 校准。

    Args:
        port: 串口设备路径。
        rate: 采集频率，单位 Hz。
        sensor: 传感器索引。
        confirm_no_load: 是否确认传感器无负载，用于 bias 校准授权。
        software_baseline: 是否启用软件基准扣除。
        baseline_duration_sec: 软件基准采样时长，单位 s。
        baseline_std_limit_n: 软件基准扰动检测阈值，单位 N。
        count: 读取样本数。
    """
    if not confirm_no_load:
        typer.secho(
            "拒绝执行：bias 校准前必须确认传感器无负载。"
            "请添加 --confirm-no-load。",
            err=True,
        )
        raise typer.Exit(code=2)
    with SensorSession(
        port,
        rate,
        sensor,
        bias=True,
        software_baseline=software_baseline,
        baseline_duration_sec=baseline_duration_sec,
        baseline_std_limit_n=baseline_std_limit_n,
    ) as session:
        _collect_samples(session, count=count, echo=True)


@app.command()
def record(
    port: Annotated[
        str,
        typer.Option("--port", "-p", help="串口设备路径"),
    ] = DEFAULT_PORT,
    rate: Annotated[
        int,
        typer.Option("--rate", "-r", help="采集频率 (100/500/1000 Hz)"),
    ] = DEFAULT_RATE_HZ,
    sensor: Annotated[
        int,
        typer.Option("--sensor", "-s", help="传感器索引 (0-9)", min=0, max=9),
    ] = DEFAULT_SENSOR,
    confirm_no_load: Annotated[
        bool,
        typer.Option(
            "--confirm-no-load",
            help="确认传感器无负载，允许执行 bias 校准",
        ),
    ] = False,
    software_baseline: Annotated[
        bool,
        typer.Option(
            "--software-baseline/--no-software-baseline",
            help="SDK bias 后采样无负载均值并在运行时扣除",
        ),
    ] = True,
    baseline_duration_sec: Annotated[
        float,
        typer.Option("--baseline-duration", help="软件基准采样时长 (秒)", min=0.1),
    ] = DEFAULT_BASELINE_DURATION_SEC,
    baseline_std_limit_n: Annotated[
        float,
        typer.Option(
            "--baseline-std-limit",
            help="软件基准扰动标准差阈值 (N)",
            min=0.001,
        ),
    ] = DEFAULT_BASELINE_STD_LIMIT_N,
    duration: Annotated[
        float,
        typer.Option("--duration", "-d", help="记录时长 (秒)", min=0.1),
    ] = 10.0,
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="CSV 输出路径"),
    ] = "data/contactile_record.csv",
) -> None:
    """采集数据并保存为 CSV 文件。

    按指定时长持续采集，同时计算并输出实际采样率统计。

    Args:
        port: 串口设备路径。
        rate: 采集频率，单位 Hz。
        sensor: 传感器索引。
        confirm_no_load: 是否确认传感器无负载，用于 bias 校准授权。
        software_baseline: 是否启用软件基准扣除。
        baseline_duration_sec: 软件基准采样时长，单位 s。
        baseline_std_limit_n: 软件基准扰动检测阈值，单位 N。
        duration: 记录时长，单位 s。
        output: CSV 输出路径。
    """
    if not confirm_no_load:
        typer.secho(
            "拒绝执行：bias 校准前必须确认传感器无负载。"
            "请添加 --confirm-no-load。",
            err=True,
        )
        raise typer.Exit(code=2)
    with SensorSession(
        port,
        rate,
        sensor,
        bias=True,
        software_baseline=software_baseline,
        baseline_duration_sec=baseline_duration_sec,
        baseline_std_limit_n=baseline_std_limit_n,
    ) as session:
        with csv_writer(output) as writer:
            typer.echo(f"记录 CSV: {output}")
            samples = _collect_samples(session, duration=duration, writer=writer)
    _summarize(samples, "Record summary")


@app.command()
def live(
    port: Annotated[
        str,
        typer.Option("--port", "-p", help="串口设备路径"),
    ] = DEFAULT_PORT,
    rate: Annotated[
        int,
        typer.Option("--rate", "-r", help="采集频率 (100/500/1000 Hz)"),
    ] = DEFAULT_RATE_HZ,
    sensor: Annotated[
        int,
        typer.Option(
            "--sensor",
            help="单传感器索引 (0-9)，未指定 --sensors 时使用",
            min=0,
            max=9,
        ),
    ] = DEFAULT_SENSOR,
    sensors_arg: Annotated[
        Optional[str],
        typer.Option("--sensors", "-s", help="同屏显示多个传感器，例如 0,1"),
    ] = None,
    confirm_no_load: Annotated[
        bool,
        typer.Option(
            "--confirm-no-load",
            help="确认传感器无负载，允许执行 bias 校准",
        ),
    ] = False,
    software_baseline: Annotated[
        bool,
        typer.Option(
            "--software-baseline/--no-software-baseline",
            help="SDK bias 后采样无负载均值并在运行时扣除",
        ),
    ] = True,
    baseline_duration_sec: Annotated[
        float,
        typer.Option("--baseline-duration", help="软件基准采样时长 (秒)", min=0.1),
    ] = DEFAULT_BASELINE_DURATION_SEC,
    baseline_std_limit_n: Annotated[
        float,
        typer.Option(
            "--baseline-std-limit",
            help="软件基准扰动标准差阈值 (N)",
            min=0.001,
        ),
    ] = DEFAULT_BASELINE_STD_LIMIT_N,
    window_sec: Annotated[
        float,
        typer.Option("--window", "-w", help="实时曲线窗口秒数", min=1.0),
    ] = DEFAULT_WINDOW_SEC,
    force_limit: Annotated[
        float,
        typer.Option("--force-limit", help="统一 Y 轴范围: -limit 到 +limit N", min=0.1),
    ] = DEFAULT_FORCE_LIMIT_N,
    viewport_width: Annotated[
        int,
        typer.Option("--width", help="窗口初始宽度", min=900),
    ] = DEFAULT_VIEWPORT_WIDTH,
    viewport_height: Annotated[
        int,
        typer.Option("--height", help="窗口初始高度", min=600),
    ] = DEFAULT_VIEWPORT_HEIGHT,
    font_size: Annotated[
        int,
        typer.Option("--font-size", help="界面字体大小", min=12, max=36),
    ] = DPG_FONT_SIZE,
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="可选 CSV 输出路径"),
    ] = None,
) -> None:
    """启动 Dear PyGui 实时力曲线面板。

    支持单传感器或多传感器（最多 2 个）同屏显示。
    采集在独立线程中进行，避免 GUI 刷新被 SDK 阻塞 I/O 卡住。

    Args:
        port: 串口设备路径。
        rate: 采集频率，单位 Hz。
        sensor: 默认单传感器索引（--sensors 未指定时使用）。
        sensors_arg: 多传感器列表，如 "0,1"。
        confirm_no_load: 是否确认传感器无负载，用于 bias 校准授权。
        software_baseline: 是否启用软件基准扣除。
        baseline_duration_sec: 软件基准采样时长，单位 s。
        baseline_std_limit_n: 软件基准扰动检测阈值，单位 N。
        window_sec: 实时曲线时间窗口，单位 s。
        force_limit: Y 轴力范围限制，单位 N。
        viewport_width: 窗口初始宽度，单位 px。
        viewport_height: 窗口初始高度，单位 px。
        font_size: 界面字体大小，单位 px。
        output: 可选 CSV 输出路径（多传感器时不写入）。
    """
    if not confirm_no_load:
        typer.secho(
            "拒绝执行：bias 校准前必须确认传感器无负载。"
            "请添加 --confirm-no-load。",
            err=True,
        )
        raise typer.Exit(code=2)
    try:
        import dearpygui.dearpygui as dpg
    except ImportError as exc:
        raise RuntimeError(
            "live 需要 Dear PyGui。请在 python_ws 下运行: uv sync"
        ) from exc

    sensors = _parse_sensor_list(sensors_arg) if sensors_arg else [sensor]
    if len(sensors) > 2:
        raise typer.BadParameter("live 最多同时显示两个传感器")
    max_samples = max(int(rate * window_sec * 1.25), rate)
    state = LiveState(max_samples=max_samples)
    worker = threading.Thread(
        target=_acquisition_worker,
        args=(
            port,
            rate,
            sensors,
            output,
            software_baseline,
            baseline_duration_sec,
            baseline_std_limit_n,
            state,
        ),
        daemon=True,
    )
    worker.start()

    if output and len(sensors) > 1:
        typer.echo(
            "提示: 多传感器 live 暂不写 CSV；"
            "如需记录，请先分别运行单传感器 --sensor。"
        )

    dpg.create_context()

    # 加载系统字体并指定字号，Dear PyGui 2.x 中以此实现全局缩放
    if os.path.exists(DPG_FONT_PATH):
        with dpg.font_registry():
            default_font = dpg.add_font(DPG_FONT_PATH, font_size)
        dpg.bind_font(default_font)

    dpg.create_viewport(
        title="Contactile 3DFBS Lab",
        width=viewport_width,
        height=viewport_height,
    )
    with dpg.window(label="Contactile 3DFBS Lab", tag="main_window"):
        dpg.add_text("启动采集...", tag="status")
        dpg.add_text("", tag="stats")
        series_tags: dict[int, dict[str, str]] = {}
        plot_tags: dict[int, str] = {}
        y_axis_tags: dict[int, str] = {}
        plot_height = max(260, int((viewport_height - 150) / len(sensors)))
        for sensor_index in sensors:
            plot_tag = f"plot_s{sensor_index}"
            y_axis_tag = f"y_axis_s{sensor_index}"
            plot_tags[sensor_index] = plot_tag
            y_axis_tags[sensor_index] = y_axis_tag
            with dpg.plot(
                label=f"S{sensor_index} Force",
                height=plot_height,
                width=-1,
                tag=plot_tag,
            ):
                dpg.add_plot_legend()
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Force (N)", tag=y_axis_tag)
                dpg.set_axis_limits(x_axis, -window_sec, 0)
                dpg.set_axis_limits(y_axis, -force_limit, force_limit)
                series_tags[sensor_index] = {
                    "fx": f"series_s{sensor_index}_fx",
                    "fy": f"series_s{sensor_index}_fy",
                    "fz": f"series_s{sensor_index}_fz",
                    "norm": f"series_s{sensor_index}_norm",
                }
                dpg.add_line_series(
                    [], [], label="Fx", parent=y_axis, tag=series_tags[sensor_index]["fx"]
                )
                dpg.add_line_series(
                    [], [], label="Fy", parent=y_axis, tag=series_tags[sensor_index]["fy"]
                )
                dpg.add_line_series(
                    [], [], label="Fz", parent=y_axis, tag=series_tags[sensor_index]["fz"]
                )
                dpg.add_line_series(
                    [], [], label="|F|", parent=y_axis, tag=series_tags[sensor_index]["norm"]
                )

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)

    try:
        frame_interval_sec = 1.0 / 60.0
        last_plot_height = 0
        while dpg.is_dearpygui_running() and not state.stop.is_set():
            frame_start = time.monotonic()
            client_height = dpg.get_viewport_client_height()
            plot_height = max(260, int((client_height - 150) / len(sensors)))
            if plot_height != last_plot_height:
                for plot_tag in plot_tags.values():
                    dpg.configure_item(plot_tag, height=plot_height, width=-1)
                last_plot_height = plot_height
            samples = state.snapshot()
            if samples:
                latest = samples[-1]
                t_latest = latest.timestamp_us
                window_start = t_latest - int(window_sec * 1_000_000)
                visible = [s for s in samples if s.timestamp_us >= window_start]
                xs = [(s.timestamp_us - t_latest) / 1_000_000.0 for s in visible]
                for sensor_index in sensors:
                    dpg.set_axis_limits(y_axis_tags[sensor_index], -force_limit, force_limit)
                    visible_sensor_samples = [
                        frame.samples[sensor_index]
                        for frame in visible
                        if sensor_index in frame.samples
                    ]
                    sensor_xs = [
                        (frame.timestamp_us - t_latest) / 1_000_000.0
                        for frame in visible
                        if sensor_index in frame.samples
                    ]
                    tags = series_tags[sensor_index]
                    dpg.set_value(tags["fx"], [sensor_xs, [s.fx for s in visible_sensor_samples]])
                    dpg.set_value(tags["fy"], [sensor_xs, [s.fy for s in visible_sensor_samples]])
                    dpg.set_value(tags["fz"], [sensor_xs, [s.fz for s in visible_sensor_samples]])
                    dpg.set_value(
                        tags["norm"],
                        [sensor_xs, [s.force_norm for s in visible_sensor_samples]],
                    )
                dpg.set_value(
                    "status",
                    f"port={port}  sensors={','.join(str(s) for s in sensors)}  "
                    f"rate={rate}Hz  samples={state.count}",
                )
                latest_stats = []
                for sensor_index in sensors:
                    sample = latest.samples.get(sensor_index)
                    if sample is not None:
                        latest_stats.append(
                            f"S{sensor_index}: Fx={sample.fx:.3f} Fy={sample.fy:.3f} "
                            f"Fz={sample.fz:.3f} |F|={sample.force_norm:.3f} N"
                        )
                dpg.set_value(
                    "stats",
                    "\n".join(latest_stats),
                )
            dpg.render_dearpygui_frame()
            elapsed = time.monotonic() - frame_start
            if elapsed < frame_interval_sec:
                time.sleep(frame_interval_sec - elapsed)
    finally:
        state.stop.set()
        worker.join(timeout=3.0)
        dpg.destroy_context()

    if state.error:
        raise RuntimeError(str(state.error)) from state.error


@app.command()
def replay(
    csv_path: Annotated[
        str,
        typer.Argument(help="CSV 文件路径", exists=True, file_okay=True, dir_okay=False),
    ],
) -> None:
    """读取 CSV 离线回放力数据曲线。

    使用 matplotlib 绘制 FX/FY/FZ 和合力随时间变化的曲线。

    Args:
        csv_path: CSV 数据文件路径。
    """
    samples = _load_csv(csv_path)
    _summarize(samples, "Replay summary")
    if not samples:
        return

    mpl_config_dir = Path("/tmp/contactile_matplotlib")
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("replay 需要 matplotlib，请先安装项目依赖") from exc

    t0 = samples[0].timestamp_us
    xs = [(s.timestamp_us - t0) / 1_000_000.0 for s in samples]
    plt.figure("Contactile Replay")
    plt.plot(xs, [s.fx for s in samples], label="Fx")
    plt.plot(xs, [s.fy for s in samples], label="Fy")
    plt.plot(xs, [s.fz for s in samples], label="Fz")
    plt.plot(xs, [s.force_norm for s in samples], label="|F|", alpha=0.65)
    plt.xlabel("Time (s)")
    plt.ylabel("Force (N)")
    plt.title(csv_path)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    if "agg" in plt.get_backend().lower():
        typer.echo("Matplotlib 使用非交互后端，已跳过窗口显示")
    else:
        plt.show()


@app.command()
def check(
    port: Annotated[
        str,
        typer.Option("--port", "-p", help="串口设备路径"),
    ] = DEFAULT_PORT,
    rate: Annotated[
        int,
        typer.Option("--rate", "-r", help="采集频率 (100/500/1000 Hz)"),
    ] = DEFAULT_RATE_HZ,
    sensor: Annotated[
        int,
        typer.Option("--sensor", "-s", help="传感器索引 (0-9)", min=0, max=9),
    ] = DEFAULT_SENSOR,
    confirm_no_load: Annotated[
        bool,
        typer.Option(
            "--confirm-no-load",
            help="确认传感器无负载，允许执行 bias 校准",
        ),
    ] = False,
    software_baseline: Annotated[
        bool,
        typer.Option(
            "--software-baseline/--no-software-baseline",
            help="SDK bias 后采样无负载均值并在运行时扣除",
        ),
    ] = True,
    baseline_duration_sec: Annotated[
        float,
        typer.Option("--baseline-duration", help="软件基准采样时长 (秒)", min=0.1),
    ] = DEFAULT_BASELINE_DURATION_SEC,
    baseline_std_limit_n: Annotated[
        float,
        typer.Option(
            "--baseline-std-limit",
            help="软件基准扰动标准差阈值 (N)",
            min=0.001,
        ),
    ] = DEFAULT_BASELINE_STD_LIMIT_N,
    duration: Annotated[
        float,
        typer.Option("--duration", "-d", help="检查时长 (秒)", min=0.1),
    ] = 5.0,
) -> None:
    """校正后残余静态噪声和采样间隔检查。

    在传感器无负载状态下采集校正后的数据，统计各轴残余噪声水平和实际
    采样间隔分布，用于评估软件基准后的传感器健康状态和连接质量。

    Args:
        port: 串口设备路径。
        rate: 采集频率，单位 Hz。
        sensor: 传感器索引。
        confirm_no_load: 是否确认传感器无负载，用于 bias 校准授权。
        software_baseline: 是否启用软件基准扣除。
        baseline_duration_sec: 软件基准采样时长，单位 s。
        baseline_std_limit_n: 软件基准扰动检测阈值，单位 N。
        duration: 检查时长，单位 s。
    """
    if not confirm_no_load:
        typer.secho(
            "拒绝执行：bias 校准前必须确认传感器无负载。"
            "请添加 --confirm-no-load。",
            err=True,
        )
        raise typer.Exit(code=2)
    with SensorSession(
        port,
        rate,
        sensor,
        bias=True,
        software_baseline=software_baseline,
        baseline_duration_sec=baseline_duration_sec,
        baseline_std_limit_n=baseline_std_limit_n,
    ) as session:
        samples = _collect_samples(session, duration=duration)
    _summarize(samples, "Check summary (corrected residual noise)")
    for axis_name, values in (
        ("fx", [s.fx for s in samples]),
        ("fy", [s.fy for s in samples]),
        ("fz", [s.fz for s in samples]),
    ):
        if values:
            typer.echo(
                f"  {axis_name} mean/stdev/min/max: "
                f"{statistics.fmean(values):.5f} / {statistics.pstdev(values):.5f} / "
                f"{min(values):.5f} / {max(values):.5f}"
            )


# ── 入口 ──────────────────────────────────────────────────────────


def main(argv: Optional[Iterable[str]] = None) -> int:
    """CLI 入口，返回 POSIX 退出码。"""
    try:
        if argv is None:
            app()
        else:
            app(args=list(argv))
    except KeyboardInterrupt:
        typer.echo("\n用户中断")
        return 130
    except Exception as exc:
        typer.secho(f"错误: {exc}", err=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

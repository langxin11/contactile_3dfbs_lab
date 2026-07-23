/**
 * Contactile 3DFBS C++ 记录与测速示例
 *
 * 编译运行:
 *   bash scripts/run_cpp.sh -- --help
 *   bash scripts/run_cpp.sh -- --confirm-no-load --duration 2 --output /tmp/cpp_rate.csv
 *
 * 不依赖 ROS2，直接链接原厂 libPTSDK.a 静态库。
 * 默认使用阻塞式 readNextSample()，避免 Python 轮询和逐帧终端打印影响采样率。
 *
 * 注意: 只 include PTSDKListener.h，不直接 include PTSDKSensor.h。
 *       后者的 include guard 存在缺陷，会导致 class redefinition 编译错误。
 */

#include <cerrno>
#include <chrono>
#include <cmath>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>

#include "PTSDKConstants.h"
#include "PTSDKListener.h"

static volatile std::sig_atomic_t g_running = 1;

struct Options {
    std::string port = "/dev/ttyACM0";
    int baud_rate = 9600;
    int sensor_index = 0;
    double duration_sec = 0.0;
    std::string output_path;
    int print_every = 0;
    bool confirm_no_load = false;
    bool bias = true;
};

class ListenerConnectionGuard {
public:
    explicit ListenerConnectionGuard(PTSDKListener *listener)
        : listener_(listener)
    {
    }

    ~ListenerConnectionGuard()
    {
        disconnect();
    }

    void disconnect()
    {
        if (listener_ != nullptr) {
            listener_->stopListeningAndDisconnect();
            listener_ = nullptr;
        }
    }

private:
    PTSDKListener *listener_;
};

void signalHandler(int)
{
    g_running = 0;
}

void printUsage(const char *program)
{
    printf("用法: %s [选项]\n", program);
    printf("\n");
    printf("选项:\n");
    printf("  --port PATH              串口设备，默认 /dev/ttyACM0\n");
    printf("  --baud-rate N            串口波特率，默认 9600\n");
    printf("  --sensor N               传感器索引 0..9，默认 0\n");
    printf("  --duration SEC           记录时长；不指定则持续运行直到 Ctrl+C\n");
    printf("  --output PATH            写入 CSV；不指定则只统计\n");
    printf("  --print-every N          每 N 个样本打印一行；默认 0 表示不逐帧打印\n");
    printf("  --confirm-no-load        确认传感器无负载，允许 bias 校准\n");
    printf("  --no-bias                跳过 bias 校准\n");
    printf("  --help                   显示帮助\n");
    printf("\n");
    printf("示例:\n");
    printf("  bash scripts/run_cpp.sh -- --confirm-no-load --duration 2 --output /tmp/cpp_rate.csv\n");
    printf("  bash scripts/run_cpp.sh -- --baud-rate 115200 --confirm-no-load --duration 2\n");
}

bool parseInt(const char *text, int *value)
{
    char *end = nullptr;
    errno = 0;
    long parsed = std::strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return false;
    }
    *value = static_cast<int>(parsed);
    return true;
}

bool parseDouble(const char *text, double *value)
{
    char *end = nullptr;
    errno = 0;
    double parsed = std::strtod(text, &end);
    if (errno != 0 || end == text || *end != '\0') {
        return false;
    }
    *value = parsed;
    return true;
}

bool requireValue(int argc, char *argv[], int index)
{
    if (index + 1 < argc) {
        return true;
    }
    fprintf(stderr, "参数缺少值: %s\n", argv[index]);
    return false;
}

bool parseArgs(int argc, char *argv[], Options *options)
{
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            std::exit(0);
        } else if (arg == "--port") {
            if (!requireValue(argc, argv, i)) {
                return false;
            }
            options->port = argv[++i];
        } else if (arg == "--baud-rate") {
            if (!requireValue(argc, argv, i) || !parseInt(argv[++i], &options->baud_rate)) {
                fprintf(stderr, "--baud-rate 必须是整数\n");
                return false;
            }
        } else if (arg == "--sensor") {
            if (!requireValue(argc, argv, i) || !parseInt(argv[++i], &options->sensor_index)) {
                fprintf(stderr, "--sensor 必须是整数\n");
                return false;
            }
        } else if (arg == "--duration") {
            if (!requireValue(argc, argv, i) || !parseDouble(argv[++i], &options->duration_sec)) {
                fprintf(stderr, "--duration 必须是秒数\n");
                return false;
            }
        } else if (arg == "--output") {
            if (!requireValue(argc, argv, i)) {
                return false;
            }
            options->output_path = argv[++i];
        } else if (arg == "--print-every") {
            if (!requireValue(argc, argv, i) || !parseInt(argv[++i], &options->print_every)) {
                fprintf(stderr, "--print-every 必须是整数\n");
                return false;
            }
        } else if (arg == "--confirm-no-load") {
            options->confirm_no_load = true;
        } else if (arg == "--no-bias") {
            options->bias = false;
        } else if (arg.rfind("-", 0) != 0 && i == 1) {
            options->port = arg;
        } else {
            fprintf(stderr, "未知参数: %s\n", arg.c_str());
            return false;
        }
    }

    if (options->sensor_index < 0 || options->sensor_index >= MAX_NSENSOR) {
        fprintf(stderr, "--sensor 必须在 0..%d 之间\n", MAX_NSENSOR - 1);
        return false;
    }
    if (options->baud_rate <= 0) {
        fprintf(stderr, "--baud-rate 必须大于 0\n");
        return false;
    }
    if (options->duration_sec < 0.0) {
        fprintf(stderr, "--duration 不能小于 0\n");
        return false;
    }
    if (options->print_every < 0) {
        fprintf(stderr, "--print-every 不能小于 0\n");
        return false;
    }
    if (options->bias && !options->confirm_no_load) {
        fprintf(stderr, "拒绝执行: bias 前必须确认传感器无负载，请添加 --confirm-no-load，或用 --no-bias 跳过。\n");
        return false;
    }
    return true;
}

int main(int argc, char *argv[])
{
    Options options;
    if (!parseArgs(argc, argv, &options)) {
        fprintf(stderr, "运行 %s --help 查看用法\n", argv[0]);
        return 2;
    }
    if (std::signal(SIGINT, signalHandler) == SIG_ERR) {
        fprintf(stderr, "无法安装 SIGINT 处理器，拒绝在无法保证串口释放时运行\n");
        return 1;
    }

    constexpr int parity = 0;
    constexpr char byte_size = 8;
    constexpr bool enable_log = false;

    printf("=== Contactile 3DFBS C++ Reader ===\n");
    printf("串口: %s @ %d baud, sensor S%d\n",
           options.port.c_str(), options.baud_rate, options.sensor_index);
    if (options.duration_sec > 0.0) {
        printf("记录时长: %.3f s\n", options.duration_sec);
    } else {
        printf("记录时长: 持续运行，按 Ctrl+C 停止\n");
    }
    if (!options.output_path.empty()) {
        printf("CSV: %s\n", options.output_path.c_str());
    }

    constexpr int N_SENSORS = MAX_NSENSOR;
    PTSDKSensor sensors[N_SENSORS];

    PTSDKListener listener(enable_log);
    for (int i = 0; i < N_SENSORS; ++i) {
        listener.addSensor(&sensors[i]);
    }

    int ret = listener.connect(options.port.c_str(), options.baud_rate, parity, byte_size);
    if (ret != 0) {
        fprintf(stderr, "串口连接失败: %s (错误码: %d)\n", options.port.c_str(), ret);
        fprintf(stderr, "提示: 检查设备是否插入，用户是否在 dialout 组\n");
        return 1;
    }
    printf("串口连接成功\n");
    ListenerConnectionGuard connection_guard(&listener);

    if (!g_running) {
        fprintf(stderr, "连接期间收到中断，停止运行\n");
        return 130;
    }

    if (options.bias) {
        printf("发送 Bias 请求，请保持传感器无负载...\n");
        if (!listener.sendBiasRequest()) {
            fprintf(stderr, "Bias 请求失败\n");
            return 1;
        }
        printf("Bias 完成\n");
    } else {
        printf("跳过 Bias\n");
    }

    if (!g_running) {
        fprintf(stderr, "Bias 期间收到中断，停止运行\n");
        return 130;
    }

    std::ofstream csv;
    if (!options.output_path.empty()) {
        csv.open(options.output_path);
        if (!csv.is_open()) {
            fprintf(stderr, "无法打开 CSV: %s\n", options.output_path.c_str());
            return 1;
        }
        csv << "timestamp_us,t_monotonic_ns,fx,fy,fz,force_norm\n";
    }

    printf("开始采样...\n");
    if (options.print_every > 0) {
        printf("%12s  %8s  %8s  %8s  %9s\n", "timestamp", "FX(N)", "FY(N)", "FZ(N)", "|F|(N)");
    }

    auto wall_start = std::chrono::steady_clock::now();
    unsigned long first_ts_us = 0;
    unsigned long last_ts_us = 0;
    unsigned long samples = 0;
    unsigned long read_failures = 0;

    while (g_running) {
        auto check_time = std::chrono::steady_clock::now();
        double wall_elapsed_sec = std::chrono::duration<double>(check_time - wall_start).count();
        if (options.duration_sec > 0.0 && wall_elapsed_sec >= options.duration_sec) {
            break;
        }

        if (!listener.readNextSample()) {
            ++read_failures;
            continue;
        }
        if (!g_running) {
            break;
        }

        auto sample_time = std::chrono::steady_clock::now();
        double force[NDIM] = {0};
        sensors[options.sensor_index].getGlobalForce(force);
        unsigned long ts_us = static_cast<unsigned long>(sensors[options.sensor_index].getTimestamp_us());
        auto host_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            sample_time.time_since_epoch()
        ).count();
        double force_norm = std::sqrt(
            force[X_IND] * force[X_IND] +
            force[Y_IND] * force[Y_IND] +
            force[Z_IND] * force[Z_IND]
        );

        if (samples == 0) {
            first_ts_us = ts_us;
        }
        last_ts_us = ts_us;
        ++samples;

        if (csv.is_open()) {
            csv << ts_us << ','
                << host_ns << ','
                << force[X_IND] << ','
                << force[Y_IND] << ','
                << force[Z_IND] << ','
                << force_norm << '\n';
        }

        if (options.print_every > 0 && samples % static_cast<unsigned long>(options.print_every) == 0) {
            printf("%12lu  %8.3f  %8.3f  %8.3f  %9.3f\n",
                   ts_us, force[X_IND], force[Y_IND], force[Z_IND], force_norm);
        }
    }

    if (csv.is_open()) {
        csv.flush();
        csv.close();
    }

    printf("断开串口...\n");
    connection_guard.disconnect();

    auto wall_end = std::chrono::steady_clock::now();
    double wall_elapsed_sec = std::chrono::duration<double>(wall_end - wall_start).count();
    double sensor_elapsed_sec = 0.0;
    if (samples > 1 && last_ts_us > first_ts_us) {
        sensor_elapsed_sec = static_cast<double>(last_ts_us - first_ts_us) / 1000000.0;
    }
    double wall_rate_hz = wall_elapsed_sec > 0.0 ? static_cast<double>(samples) / wall_elapsed_sec : 0.0;
    double sensor_rate_hz = sensor_elapsed_sec > 0.0 ?
        static_cast<double>(samples - 1) / sensor_elapsed_sec : 0.0;

    printf("\nC++ summary:\n");
    printf("  samples: %lu\n", samples);
    printf("  read failures: %lu\n", read_failures);
    printf("  wall elapsed: %.6f s\n", wall_elapsed_sec);
    printf("  sensor elapsed: %.6f s\n", sensor_elapsed_sec);
    printf("  wall rate: %.1f Hz\n", wall_rate_hz);
    printf("  sensor timestamp rate: %.1f Hz\n", sensor_rate_hz);
    printf("退出\n");
    return 0;
}

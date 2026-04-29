/**
 * Contactile 3DFBS C++ 最小读取器
 *
 * 编译: mkdir -p cpp_ws/build && cd cpp_ws/build && cmake ../src && make
 * 运行: ./minimal_reader [/dev/ttyACM0]
 *
 * 不依赖 ROS2，直接链接原厂 libPTSDK.a 静态库。
 * 持续从 DEV001 读取传感器数据并打印到终端。
 *
 * 注意: 只 include PTSDKListener.h，不直接 include PTSDKSensor.h。
 *        后者的 include guard 存在缺陷，会导致 class 重定义编译错误。
 */

#include <cstdio>
#include <cstdlib>
#include <csignal>
#include <string>

#include "PTSDKConstants.h"
#include "PTSDKListener.h"

// 全局标志，用于 Ctrl+C 安全退出
static volatile bool g_running = true;

void signalHandler(int) {
    g_running = false;
}

int main(int argc, char *argv[])
{
    // ---- 参数 ----
    std::string port = (argc > 1) ? argv[1] : "/dev/ttyACM0";
    int baud_rate = 9600;
    int parity = 0;
    char byte_size = 8;
    bool enable_log = false;

    printf("=== Contactile 3DFBS C++ Minimal Reader ===\n");
    printf("串口: %s @ %d baud\n", port.c_str(), baud_rate);

    // ---- 传感器对象（必须创建 10 个，兼容原厂报文格式）----
    constexpr int N_SENSORS = MAX_NSENSOR;
    PTSDKSensor sensors[N_SENSORS];  // S0..S9

    // ---- Listener ----
    PTSDKListener listener(enable_log);
    for (int i = 0; i < N_SENSORS; ++i) {
        listener.addSensor(&sensors[i]);
    }

    // ---- 连接串口 ----
    int ret = listener.connect(port.c_str(), baud_rate, parity, byte_size);
    if (ret != 0) {
        fprintf(stderr, "串口连接失败: %s (错误码: %d)\n", port.c_str(), ret);
        fprintf(stderr, "提示: 检查设备是否插入，用户是否在 dialout 组\n");
        return 1;
    }
    printf("串口连接成功\n");

    // ---- Bias 校准 ----
    printf("发送 Bias 请求，请保持传感器无负载约 2 秒...\n");
    if (!listener.sendBiasRequest()) {
        fprintf(stderr, "Bias 请求失败\n");
        listener.disconnect();
        return 1;
    }
    printf("Bias 完成\n");

    // ---- 主循环：读取并打印 ----
    signal(SIGINT, signalHandler);
    printf("\n按 Ctrl+C 停止\n");
    printf("%12s  %8s  %8s  %8s\n", "timestamp", "FX(N)", "FY(N)", "FZ(N)");

    int sample_count = 0;
    while (g_running) {
        if (listener.readNextSample()) {
            double force[NDIM] = {0};
            sensors[0].getGlobalForce(force);
            auto ts_us = sensors[0].getTimestamp_us();

            printf("%12lu  %8.3f  %8.3f  %8.3f\n",
                   static_cast<unsigned long>(ts_us),
                   force[X_IND], force[Y_IND], force[Z_IND]);

            if (++sample_count >= 1000) {
                sample_count = 0;  // 持续打印，不限制
            }
        }
        // 单线程模式是阻塞读取，无需 sleep
    }

    // ---- 断开 ----
    printf("\n断开串口...\n");
    listener.disconnect();
    printf("退出\n");
    return 0;
}

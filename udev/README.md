# DEV001 udev 规则

这个目录用于管理 Contactile DEV001 串口设备的 `udev` 规则。

当前规则文件:

- `99-contactile-dev001.rules`

## 规则作用

当前规则会匹配 DEV001 的 USB 串口设备:

- `idVendor == 303a`
- `idProduct == 4001`

并执行两件事:

1. 创建稳定的设备别名 `/dev/contactile_dev001`
2. 将设备权限设置为 `0666`

规则内容见 [99-contactile-dev001.rules](/home/xiaodalaing/project/contactile_3dfbs_lab/udev/99-contactile-dev001.rules:1)。

## 为什么要用 udev

默认串口名通常是 `/dev/ttyACM0`，但它有两个问题:

- 设备重插后编号可能变化
- 普通用户可能没有访问权限，程序会报 `Permission denied`

`udev` 规则可以同时解决这两个问题。

## 安装

将规则复制到系统目录并重新加载:

```bash
sudo cp udev/99-contactile-dev001.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

然后拔插一次 DEV001，或重新连接 USB。

## 验证

检查规则是否生效:

```bash
ls -l /dev/contactile_dev001
ls -l /dev/ttyACM0
```

如果成功，你应该能看到:

- `/dev/contactile_dev001` 存在
- 它指向真实设备 `ttyACM*`
- 权限允许当前用户访问

也可以进一步确认设备属性:

```bash
udevadm info -a -n /dev/ttyACM0 | grep -E 'idVendor|idProduct'
```

## 使用建议

安装规则后，建议项目脚本和配置优先使用:

```bash
/dev/contactile_dev001
```

这样比直接写 `/dev/ttyACM0` 更稳定。

## 权限策略说明

当前规则使用:

```udev
MODE="0666"
```

这表示本机所有用户都可读写该串口，适合个人开发机快速验证。

如果你希望权限更收敛，可以改成:

```udev
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="4001", SYMLINK+="contactile_dev001", GROUP="dialout", MODE="0660"
```

此时仍需确保当前用户属于 `dialout` 组:

```bash
sudo usermod -aG dialout $USER
```

然后注销并重新登录。

## 常见问题

`/dev/contactile_dev001` 没出现:

- 确认设备已经重新插拔
- 确认规则已复制到 `/etc/udev/rules.d/`
- 确认 `idVendor` 和 `idProduct` 与当前设备一致

仍然提示 `Permission denied`:

- 检查规则是否真的生效
- 用 `ls -l /dev/ttyACM0 /dev/contactile_dev001` 看最终权限
- 如果你改用了 `GROUP="dialout"`，确认当前会话已经重新登录

# GT06

中文 | [English](./README.md)

## 概述

- GT06 为通用车载 GPS 定位通信协议，基于 TCP 协议实现。
- 该项目基于 QuecPython 实现了 GT06 协议**客户端**功能，用户可直接使用该功能与对应服务端进行标准内的数据交互。

**主要功能：**

- 终端登录
- 终端 GPS & LBS 定位信息上报
- 终端设备状态信息上报
- 服务端指令下发与应答

## 用法

- [API 参考手册](./docs/zh/API参考手册.md)
- [用户使用手册](./docs/zh/用户使用手册.md)
- [客户端示例代码](./code/test_gt06.py)

## 贡献

我们欢迎对本项目的改进做出贡献！请按照以下步骤进行贡献：

1. Fork 此仓库。
2. 创建一个新分支（`git checkout -b feature/your-feature`）。
3. 提交您的更改（`git commit -m 'Add your feature'`）。
4. 推送到分支（`git push origin feature/your-feature`）。
5. 打开一个 Pull Request。

## 许可证

本项目使用 Apache 许可证。详细信息请参阅 [LICENSE](./LICENSE) 文件。

## 支持

如果您有任何问题或需要支持，请参阅 [QuecPython 文档](https://python.quectel.com/doc) 或在本仓库中打开一个 issue。

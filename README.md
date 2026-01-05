# iTrigger-Music

用 iPhone 快捷指令远程控制 Windows 电脑自动播放网易云音乐。

> 通过 iOS 自动化（Shortcuts）发送一个信号，PC 接收后自动启动网易云音乐、设置音量并开始播放 —— 全程无需手动操作！

![Demo Placeholder](https://via.placeholder.com/600x300?text=iPhone+→+PC+Music+Automation)

---

## 功能特性

- ✅ 一键从 iPhone 触发 PC 播放音乐  
- ✅ 自动启动网易云音乐（若未运行）  
- ✅ 可配置系统音量（如设为 60%）  
- ✅ 通过安全 Token 防止未授权访问  
- ✅ 基于局域网通信，低延迟、高隐私  

---

## 技术栈

| 组件         | 技术                                      |
|--------------|-------------------------------------------|
| 手机端       | iOS Shortcuts（快捷指令）                 |
| 通信协议     | HTTP POST（局域网）                       |
| PC 服务端    | Python + Flask                            |
| 窗口控制     | `pygetwindow` + `pyautogui`               |
| 音量控制     | `pycaw`（Windows Core Audio API）         |
| 支持系统     | **Windows 10/11**（需安装网易云音乐桌面版）|

> ⚠️ 注意：macOS 用户因无官方网易云客户端，本方案暂不支持。

---

## 安装依赖

在 Windows PC 上执行：

```bash
pip install flask pygetwindow pyautogui pycaw

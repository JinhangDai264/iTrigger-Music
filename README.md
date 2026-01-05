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

配置步骤
1. 修改网易云音乐路径（可选）
编辑 server.py，更新以下路径为你本地的实际安装位置：

Python
编辑
NETEASE_PATH = r"C:\Program Files\Netease\CloudMusic\cloudmusic.exe"
2. 设置安全 Token（推荐）
在 server.py 中修改：

Python
编辑
SECRET_TOKEN = "my_music_token_123"
建议使用强随机字符串，如 "iphone_music_2026_xyz!@#"。

3. 获取 PC 局域网 IP
在命令提示符运行：

Cmd
编辑
ipconfig
记下 IPv4 地址，例如：192.168.1.105

iPhone 快捷指令设置
打开 快捷指令 App
点击「+」创建新自动化 → 选择「手动」
添加以下操作：
URL：http://192.168.1.105:5000/play（替换为你的 IP）
设定请求体 → 类型选 JSON，内容：
Json
编辑
{"token": "my_music_token_123"}
获取 URL 内容 → 方法选 POST
关闭「运行前询问」
保存为「播放网易云」
✅ 现在点击该快捷指令，即可远程触发电脑播歌！

启动服务
在 PC 上运行：

Bash
编辑
python server.py
成功启动后，终端将显示：

Text
编辑
Running on http://0.0.0.0:5000
🔒 首次运行时，Windows 防火墙可能会弹出提示，请允许访问。

安全提示
本服务仅限 局域网内使用。
切勿将 5000 端口暴露到公网。
Token 是基础防护，请勿使用简单值。
测试接口（可选）
使用 curl 测试：

Bash
编辑
curl -X POST http://192.168.1.105:5000/play \
  -H "Content-Type: application/json" \
  -d '{"token":"my_music_token_123"}'
成功响应：

Json
编辑
{"status": "success", "msg": "Music started!"}
扩展方向
支持传参：{"action": "next", "volume": 0.7}
控制其他音乐软件（QQ 音乐、Spotify）
结合语音助手（Siri + 快捷指令）
添加日志记录或通知反馈
许可证
本项目采用 MIT 许可证。

致谢
灵感源于一个简单的愿望：

“我不想碰键盘，只想点一下手机就听歌。”

🎧 现在，躺床上点一下手机，电脑自动为你播放今日推荐吧！
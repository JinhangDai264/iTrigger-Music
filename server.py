import os
import time
import subprocess
import json
from flask import Flask, request
# 音量控制库
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
# 窗口控制库
import pygetwindow as gw
import pyautogui # 用于模拟按键

# --- 导入 pynput ---
from pynput.keyboard import Key, Controller
keyboard_controller = Controller()
# --- 导入 pynput 结束 ---

app = Flask(__name__)

# --- 配置项 ---
# 请将 YOUR_SECRET_TOKEN 替换为您自己设置的安全令牌
SECURE_TOKEN = "aaa" # 确保这里是您的令牌
# 修改此行：只保留可执行文件名，而不是完整路径
NETEASE_MUSIC_EXE_PATH = "cloudmusic.exe" # 网易云音乐的默认进程名
# 如果上面的不行，再尝试完整路径（但检查函数也要用进程名）
NETEASE_MUSIC_FULL_PATH = r"F:\myApps\Netease\CloudMusic\cloudmusic.exe" # 保留完整路径用于启动
# 设置目标音量 (0.0 到 1.0 之间)
TARGET_VOLUME = 0.40 
# Flask 服务器监听的 IP 和 端口，请确保与 iPhone 快捷指令中设置的一致
HOST = '0.0.0.0' # 让服务器监听所有可用网络接口，以便局域网内其他设备可以访问
PORT = 5000
# --- 配置项结束 ---

def set_system_volume(volume_level):
    """
    设置 Windows 系统主音量
    volume_level: float, 0.0 (静音) 到 1.0 (最大音量)
    """
    try:
        from comtypes import CoInitialize, CoUninitialize
        CoInitialize() # 初始化 COM

        # 获取默认音频输出设备
        devices = AudioUtilities.GetSpeakers()
        if not devices:
            print("[ERROR] 无法获取音频输出设备")
            return

        # 激活 IAudioEndpointVolume 接口
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # 设置音量，范围是 0.0 到 1.0
        volume.SetMasterVolumeLevelScalar(volume_level, None)
        print(f"[INFO] 系统音量已设置为 {volume_level:.0%}")
        
        CoUninitialize() # 反初始化 COM
        
    except AttributeError as e:
        print(f"[ERROR] pycaw 音量控制库属性错误: {e}. 可能是库版本或系统兼容性问题。")
        try:
            CoUninitialize()
        except:
            pass
    except Exception as e:
        print(f"[ERROR] 设置系统音量失败: {e}")
        try:
            CoUninitialize()
        except:
            pass

def is_process_running(process_name):
    """
    检查指定进程是否正在运行
    process_name: str, 进程的可执行文件名，例如 "notepad.exe"
    """
    try:
        # 获取所有正在运行的进程
        processes = subprocess.check_output(['tasklist'])
        # 检查目标进程名是否在列表中
        if process_name.encode('utf-8') in processes:
            return True
        return False
    except subprocess.CalledProcessError:
        # tasklist 命令出错时的处理
        return False

def bring_window_to_front(window_title_keyword):
    """
    将包含特定关键词的窗口带到前台并激活
    window_title_keyword: str, 用于查找窗口标题的关键词
    """
    try:
        # 等待一下，确保窗口标题已经加载完全
        time.sleep(0.5)
        print(f"[DEBUG] 查找包含 '{window_title_keyword}' 的窗口...")
        
        # 查找标题中包含关键词的窗口
        windows = gw.getWindowsWithTitle(window_title_keyword)
        print(f"[DEBUG] 找到 {len(windows)} 个匹配的窗口: {[w.title for w in windows]}")
        
        if windows:
            # 获取第一个匹配的窗口
            window = windows[0]
            print(f"[DEBUG] 尝试操作窗口: '{window.title}'")
            # 修复: 移除不存在的属性检查
            print(f"[DEBUG] 窗口状态 - isMinimized: {window.isMinimized}, isMaximized: {window.isMaximized}")
            
            # 检查窗口是否被最小化，如果是则恢复
            if window.isMinimized:
                print(f"[DEBUG] 窗口 '{window.title}' 已最小化，正在恢复...")
                window.restore() # 恢复窗口
                time.sleep(1) # 等待恢复完成
            else:
                print(f"[DEBUG] 窗口 '{window.title}' 未最小化。")

            # 检查窗口是否被最大化
            if window.isMaximized:
                print(f"[DEBUG] 窗口 '{window.title}' 已最大化。")
            else:
                print(f"[DEBUG] 窗口 '{window.title}' 未最大化。")

            # 将窗口带到前台并激活
            print(f"[DEBUG] 尝试激活窗口: '{window.title}'")
            window.activate() # 激活窗口5
            
            # 尝试获取焦点 (在某些情况下可能更有效)
            # window.focus() # 可选，如果 activate 不够
            
            print(f"[INFO] 窗口 '{window.title}' 已激活并带到前台")
            return True
        else:
            print(f"[INFO] 未找到标题包含 '{window_title_keyword}' 的窗口")
            return False
    except Exception as e:
        print(f"[ERROR] 激活窗口失败: {e}")
        import traceback
        traceback.print_exc() # 打印详细错误
        return False

def send_play_pause_key():
    """
    模拟发送空格键，网易云音乐通常用空格键控制播放/暂停
    """
    try:
        # 确保网易云音乐窗口是活动窗口，然后发送空格键
        pyautogui.press('space')
        print("[INFO] 播放/暂停命令已发送 (空格键)")
    except Exception as e:
        print(f"[ERROR] 发送按键失败: {e}")

@app.route('/trigger_music', methods=['POST'])
def trigger_music():
    """
    Flask 路由，处理来自 iPhone 的 POST 请求
    """
    try:
        # --- 添加调试信息 ---
        print("--- Debug Info Start ---")
        received_token = request.headers.get('Authorization')
        print(f"Received Authorization Header: '{received_token}'")
        expected_token = f"Bearer {SECURE_TOKEN}"
        print(f"Expected Token: '{expected_token}'")
        print(f"Tokens Match: {received_token == expected_token}")
        print("--- Debug Info End ---")

        # 1. 验证安全令牌
        token = request.headers.get('Authorization')
        if token != f"Bearer {SECURE_TOKEN}":
            print(f"[WARNING] 收到未授权请求，收到令牌: {repr(token)}, 期望令牌: {repr(f'Bearer {SECURE_TOKEN}')}")
            return json.dumps({"status": "error", "message": "Unauthorized"}), 401, {'Content-Type': 'application/json'}

        print("[INFO] 收到授权请求，开始执行音乐播放流程...")

        # 2. 检查网易云音乐是否正在运行
        # 修改：使用进程名检查
        is_running = is_process_running(NETEASE_MUSIC_EXE_PATH)
        print(f"[DEBUG] 检查进程 '{NETEASE_MUSIC_EXE_PATH}' 运行状态: {is_running}")
        if not is_running:
            print("[INFO] 网易云音乐未运行，正在启动...")
            # 修改：使用完整路径启动
            proc = subprocess.Popen([NETEASE_MUSIC_FULL_PATH])
            print(f"[DEBUG] 启动进程 PID: {proc.pid}")
            # 给程序一些时间启动，可以适当调整
            print("[DEBUG] 等待程序启动 (sleep 10秒)...")
            time.sleep(10) # 增加等待时间
            print("[DEBUG] 等待结束，检查是否已运行...")
            # 修改：使用进程名再次检查
            is_running_after_start = is_process_running(NETEASE_MUSIC_EXE_PATH)
            print(f"[DEBUG] 启动后检查进程 '{NETEASE_MUSIC_EXE_PATH}' 运行状态: {is_running_after_start}")
            # 如果启动后仍未运行，给出警告并跳过后续步骤
            if not is_running_after_start:
                print("[ERROR] 网易云音乐启动失败，无法继续执行后续操作。")
                return json.dumps({"status": "error", "message": "Failed to start Netease Cloud Music"}), 500, {'Content-Type': 'application/json'}
        else:
            print("[INFO] 网易云音乐已在运行")

        # 3. 设置音量
        print(f"[DEBUG] 开始设置系统音量为 {TARGET_VOLUME:.0%}")
        try:
            set_system_volume(TARGET_VOLUME)
            print("[DEBUG] 系统音量设置完成")
        except Exception as e:
            print(f"[ERROR] 设置系统音量过程中发生异常: {e}")

        # 4. (可选) 尝试将网易云音乐窗口带到前台 (如果需要，可以保留)
        # print("[DEBUG] 开始查找并激活网易云音乐窗口...")
        # # 网易云音乐的窗口标题通常是 "歌曲名 - 歌手名" 或包含 "网易云音乐" / "CloudMusic"
        # # 尝试查找包含 " - " 的窗口，这通常是音乐播放器的格式
        # # 或者尝试查找可能的通用关键词
        # keywords_to_try = [
        #     "网易云音乐", # 尝试主标题
        #     "CloudMusic", # 尝试英文名
        #     " - ",        # 尝试通用音乐格式 "歌曲名 - 歌手名"
        #     "NetEase",    # 尝试品牌名
        # ]
        #
        # window_found = False
        # for keyword in keywords_to_try:
        #     if bring_window_to_front(keyword):
        #         window_found = True
        #         break
        #
        # if not window_found:
        #     print("[WARNING] 未能找到并激活网易云音乐窗口。")
        # else:
        #     print("[DEBUG] 成功激活网易云音乐窗口")

        # 5. 稍作延迟，确保程序已准备好接收快捷键 (可选，但建议)
        print("[DEBUG] 等待 1 秒，确保程序就绪...")
        time.sleep(1)

        # --- 使用全局快捷键 Ctrl+Alt+P 播放/暂停 ---
        print("[DEBUG] 准备发送全局播放/暂停命令 (Ctrl+Alt+P)...")
        try:
            # 按下 Ctrl + Alt + P
            keyboard_controller.press(Key.ctrl_l) # 使用左 Ctrl，避免干扰
            keyboard_controller.press(Key.alt_l)  # 使用左 Alt，避免干扰
            keyboard_controller.press('p')
            # 释放按键 (按相反顺序)
            keyboard_controller.release('p')
            keyboard_controller.release(Key.alt_l)
            keyboard_controller.release(Key.ctrl_l)
            print("[INFO] 全局播放/暂停命令已发送 (Ctrl+Alt+P)")
        except Exception as e:
            print(f"[ERROR] 发送全局播放/暂停按键过程中发生异常: {e}")

        print("[INFO] 音乐触发流程执行完毕")
        return json.dumps({"status": "success", "message": "Music playback triggered successfully"}), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"[ERROR] 处理请求时发生异常: {e}")
        import traceback
        traceback.print_exc() # 打印完整的错误堆栈
        return json.dumps({"status": "error", "message": "Internal Server Error"}), 500, {'Content-Type': 'application/json'}
    
if __name__ == '__main__':
    print(f"[INFO] iTrigger-Music 服务器即将启动...")
    print(f"[INFO] 请确保 iPhone 快捷指令中的 URL 为: http://<PC的局域网IP>:{PORT}/trigger_music")
    print(f"[INFO] 请确保 iPhone 快捷指令中的 Authorization Header 为: Bearer {SECURE_TOKEN}")
    app.run(host=HOST, port=PORT, debug=False) # debug=False 用于生产环境
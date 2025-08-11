import subprocess
import math
import psutil
import os

CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROME_USER_DATA_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome')


def get_running_profile_windows():
    """
    返回所有已打开的Chrome Profile及其进程pid
    返回列表：[{'profile_dir': 'Profile 1', 'pid': 12345}]
    """
    result = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if p.info['name'] == 'Google Chrome' and '--profile-directory=' in ' '.join(p.info['cmdline']):
                for arg in p.info['cmdline']:
                    if arg.startswith('--profile-directory='):
                        profile_dir = arg.split('=')[1]
                        result.append({'profile_dir': profile_dir, 'pid': p.info['pid']})
        except Exception:
            continue
    return result


def arrange_windows_grid(profile_dirs):
    """
    排列所有 Chrome 窗口 - 自动计算窗口大小和位置，实现自适应屏幕均匀排列
    """
    if not profile_dirs:
        return '未选择任何窗口进行排列'

    # 获取屏幕分辨率
    screen_width = 1920
    screen_height = 1080

    # 计算窗口大小和位置
    window_count = len(profile_dirs)
    window_width = math.floor(screen_width / math.ceil(math.sqrt(window_count)))
    window_height = math.floor(screen_height / math.ceil(math.sqrt(window_count)))

    # 使用 AppleScript 排列窗口
    script_arrange = '''
tell application "Google Chrome"
    set winCount to count of windows
    if winCount = 0 then return "未找到Chrome窗口"
    tell application "Finder"
        set screenBounds to bounds of window of desktop
        set screenWidth to item 3 of screenBounds
        set screenHeight to item 4 of screenBounds
    end tell
    set colCount to (round (winCount ^ 0.5) rounding up)
    set rowCount to (winCount div colCount)
    if (winCount mod colCount) > 0 then set rowCount to rowCount + 1
    set winWidth to screenWidth / colCount
    set winHeight to screenHeight / rowCount
    repeat with i from 1 to winCount
        set col to (i - 1) mod colCount
        set row to (i - 1) div colCount
        set leftPos to (col * winWidth)
        set topPos to (row * winHeight)
        set rightPos to (leftPos + winWidth)
        set bottomPos to (topPos + winHeight)
        set bounds of window i to {leftPos, topPos, rightPos, bottomPos}
    end repeat
    activate -- 让所有窗口置顶显示
end tell
'''

    subprocess.run(['osascript', '-e', script_arrange])
    return f"已排列{len(profile_dirs)}个窗口"

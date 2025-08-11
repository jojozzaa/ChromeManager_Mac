import os
import subprocess
from pathlib import Path

CHROME_USER_DATA_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome')
CHROME_APP_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

class ChromeProfile:
    def __init__(self, name, path, status="未打开"):
        self.name = name
        self.path = path
        self.status = status
        self.profile_dir = os.path.basename(path)

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "path": self.path,
            "profile_dir": self.profile_dir
        }

def list_profiles():
    """
    扫描本机所有 Chrome Profile 目录，返回 ChromeProfile 列表
    """
    profiles = []
    if not os.path.exists(CHROME_USER_DATA_PATH):
        return profiles
    for entry in os.listdir(CHROME_USER_DATA_PATH):
        entry_path = os.path.join(CHROME_USER_DATA_PATH, entry)
        if os.path.isdir(entry_path) and (entry.startswith('Profile') or entry == 'Default'):
            # 优先读取Preferences文件中的自定义名称
            preferences_path = os.path.join(entry_path, 'Preferences')
            display_name = entry if entry != 'Default' else 'Default（默认）'
            if os.path.exists(preferences_path):
                try:
                    import json
                    with open(preferences_path, 'r', encoding='utf-8') as f:
                        pref = json.load(f)
                        profile_info = pref.get('profile', {})
                        custom_name = profile_info.get('name')
                        if custom_name:
                            display_name = custom_name
                except Exception:
                    pass
            # 检测 Profile 是否已打开
            status = "已打开" if is_profile_running(entry_path) else "未打开"
            profiles.append(ChromeProfile(display_name, entry_path, status))
    return profiles

def is_profile_running(profile_path):
    """
    判断某个 Profile 是否已打开（通过检测进程已打开的文件）
    """
    import psutil
    import os
    
    # 获取 Profile 目录名（如 'Profile 37'）
    profile_dir = os.path.basename(profile_path)
    # 构建完整的 Profile 路径
    full_profile_path = os.path.join(os.path.expanduser('~/Library/Application Support/Google/Chrome'), profile_dir)
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                # 检查进程打开的文件是否包含该 Profile 目录
                for f in proc.open_files():
                    if full_profile_path in f.path:
                        return True
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return False

def open_profile(profile_dir):
    """
    启动指定 Profile 的 Chrome 窗口（独立进程模式，每次都新开实例）
    """
    import subprocess
    import sys
    if sys.platform == 'darwin':
        # macOS 独立进程启动
        cmd = [
            'open', '-na', 'Google Chrome', '--args',
            f'--profile-directory={os.path.basename(profile_dir)}'
        ]
        subprocess.Popen(cmd)
    else:
        # 其它平台略
        pass

def batch_open_profiles(profile_dirs):
    for pdir in profile_dirs:
        open_profile(pdir)

def save_profile_name(profile_dir, new_name):
    """
    将new_name写入指定Profile目录下的Preferences文件（profile.name）
    """
    import json
    profile_path = os.path.join(CHROME_USER_DATA_PATH, profile_dir)
    preferences_path = os.path.join(profile_path, 'Preferences')
    if not os.path.exists(preferences_path):
        return False
    try:
        with open(preferences_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'profile' not in data:
            data['profile'] = {}
        data['profile']['name'] = new_name
        with open(preferences_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

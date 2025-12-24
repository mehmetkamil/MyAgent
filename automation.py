import os
import subprocess
import webbrowser
import difflib
import time
import psutil
import pyautogui
import ctypes  # Required to manage Windows windows

class AutomationAgent:
    def __init__(self):
        self.app_paths = {}
        self.common_sites = {
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "google": "https://www.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "chatgpt": "https://chatgpt.com"
        }
        self.scan_installed_apps()

    def scan_installed_apps(self):
        # (Remains the same, just ensuring Chrome path)
        print("📂 Scanning system...")
        paths = [r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
                 os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")]

        for path in paths:
            if not os.path.exists(path): continue
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".lnk"):
                        name = file.lower().replace(".lnk", "").replace(" ", "")
                        self.app_paths[name] = os.path.join(root, file)

        # Manual additions
        self.app_paths.update({
            "notepad": "notepad.exe", "calc": "calc.exe", "chrome": "chrome.exe",
            "vscode": "code.exe", "code": "code.exe", "cmd": "cmd.exe"
        })

    def focus_window(self, window_name):
        """
        Brings the specified window to the foreground using Windows API.
        Required for sent keys to work!
        """
        user32 = ctypes.windll.user32

        def callback(hwnd, windows):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()

                # Is the searched word in the window title? (e.g., 'chrome')
                if window_name.lower() in title:
                    windows.append(hwnd)
            return True

        windows = []
        user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.py_object)(callback), windows)

        if windows:
            hwnd = windows[0] # Take the first one found
            # Restore if minimized (SW_RESTORE = 9)
            user32.ShowWindow(hwnd, 9)
            # Bring to foreground
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.2) # Wait for Windows animation
            return True
        return False

    def execute_tool_call(self, tool_name, tool_args):
        print(f"🔧 OPERATION: {tool_name} -> {tool_args}")
        try:
            if tool_name == "chrome_control": # NEW FUNCTION
                return self.chrome_control(tool_args.get("command"))
            elif tool_name == "open_app":
                return self.open_app(tool_args.get("app_name"))
            elif tool_name == "close_app":
                return self.close_app(tool_args.get("app_name"))
            elif tool_name == "check_running":
                return self.check_running_apps()
            elif tool_name == "open_website":
                return self.open_website(tool_args.get("url"))
            elif tool_name == "system_control":
                return self.system_control(tool_args.get("action"))
        except Exception as e:
            return f"❌ Error: {e}"
        return "Unknown operation."

    def chrome_control(self, command):
        """Manages Chrome-specific commands"""
        # 1. First bring Chrome to foreground
        if not self.focus_window("chrome") and not self.focus_window("google chrome"):
            # Try to open if Chrome is not open
            self.open_app("chrome")
            time.sleep(2) # Wait for it to open

        # 2. Send the command
        try:
            if command == "new_tab":
                pyautogui.hotkey('ctrl', 't')
                return "✅ New tab opened."
            elif command == "close_tab":
                pyautogui.hotkey('ctrl', 'w')
                return "✅ Tab closed."
            elif command == "reopen_tab":
                pyautogui.hotkey('ctrl', 'shift', 't')
                return "✅ Closed tab restored."
            elif command == "next_tab":
                pyautogui.hotkey('ctrl', 'tab')
                return "➡️ Switched to next tab."
            elif command == "prev_tab":
                pyautogui.hotkey('ctrl', 'shift', 'tab')
                return "⬅️ Switched to previous tab."
            elif command == "history":
                pyautogui.hotkey('ctrl', 'h')
                return "📜 History opened."
            elif command == "downloads":
                pyautogui.hotkey('ctrl', 'j')
                return "⬇️ Downloads opened."
            elif command == "incognito":
                pyautogui.hotkey('ctrl', 'shift', 'n')
                return "🕵️ Incognito tab opened."
            elif command == "refresh":
                pyautogui.hotkey('f5')
                return "🔄 Page refreshed."
            elif command == "focus_url":
                pyautogui.hotkey('alt', 'd') # Focus on URL bar
                return "URL bar selected."
        except Exception as e:
            return f"Chrome error: {e}"
        return "Operation complete."

    def check_running_apps(self):
        running = []
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower().replace(".exe", "")
                if name in self.app_paths and name not in running:
                    running.append(name)
        except: pass
        if running: return f"🖥️ Running apps: {', '.join(running[:15])}"
        return "No important running apps found."

    def open_app(self, app_name):
        if not app_name: return "No name provided."
        name = app_name.lower().replace(" ", "")

        if name in self.common_sites:
            return self.open_website(self.common_sites[name])

        if name in self.app_paths:
            os.startfile(self.app_paths[name])
            return f"✅ {app_name} opened."

        matches = difflib.get_close_matches(name, self.app_paths.keys(), n=1, cutoff=0.5)
        if matches:
            os.startfile(self.app_paths[matches[0]])
            return f"✅ {matches[0]} opened."

        try:
            subprocess.Popen(name, shell=True)
            return f"✅ {app_name} command executed."
        except:
            return f"❌ {app_name} not found."

    def open_website(self, url):
        if not url.startswith("http"): url = "https://" + url
        webbrowser.open(url)
        return f"🌐 Site opened: {url}"

    def close_app(self, app_name):
        name = app_name.lower().replace(" ", "")
        count = 0
        for proc in psutil.process_iter(['name']):
            if name in proc.info['name'].lower():
                proc.terminate()
                count += 1
        if count > 0: return f"🚫 {app_name} closed."
        return f"⚠️ {app_name} is already closed."

    def system_control(self, action):
        if action == "shutdown": os.system("shutdown /s /t 10")
        elif action == "restart": os.system("shutdown /r /t 10")
        return f"System: {action}"

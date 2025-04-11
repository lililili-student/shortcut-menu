import tkinter as tk
from tkinter import ttk
import configparser
import os
import subprocess
from pynput import mouse
import threading
import pyautogui

# 配置文件路径
CONFIG_FILE = "shortcuts.ini"

class ShortcutApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        self.shortcuts = []
        self.load_config()
        
        # 创建鼠标监听器
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE, encoding='utf-8')
            if 'Shortcuts' in config:
                for key in config['Shortcuts']:
                    value = config['Shortcuts'][key]
                    if '|' in value:
                        name, command = value.split('|', 1)
                        self.shortcuts.append((name.strip(), command.strip()))
        else:
            # 创建默认配置
            self.shortcuts = [
                ('记事本', 'notepad.exe'),
                ('计算器', 'calc.exe')
            ]
            self.create_default_config()

    def create_default_config(self):
        """创建默认配置文件"""
        config = configparser.ConfigParser()
        config['Shortcuts'] = {
            'Item1': '记事本 | notepad.exe',
            'Item2': '计算器 | calc.exe'
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)

    def on_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if pressed and button == mouse.Button.x2:  # 检测右侧侧键
            self.show_menu(x, y)  

    def show_menu(self, x, y):
        """显示快捷菜单"""
        popup = tk.Toplevel()
        popup.wm_overrideredirect(True)  # 无边框窗口
        popup.geometry(f"+{x}+{y}")  # 设置窗口位置

        # 创建列表框
        listbox = tk.Listbox(popup, width=20, height=10)
        listbox.pack()
        def close_window():
            popup.destroy()
        # 添加快捷方式
        for name, _ in self.shortcuts:
            listbox.insert(tk.END, name)

        # 绑定双击事件
        listbox.bind('<Double-Button-1>', lambda e: self.execute_command(listbox, popup),close_window)
        
        # 绑定失去焦点事件
        popup.bind('<FocusOut>', lambda e: popup.destroy())

        # 临时重新启用监听器
        self.restart_listener(popup)

    def restart_listener(self, popup):
        """窗口关闭后重新启用监听"""
        def check_window():
            if not popup.winfo_exists():
                self.listener = mouse.Listener(on_click=self.on_click)
                self.listener.start()
        popup.after(100, check_window)

    def execute_command(self, listbox, popup):
        """执行选中命令"""
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.shortcuts):
                _, command = self.shortcuts[index]
                subprocess.Popen(command, shell=True)
        popup.destroy()

    def run(self):
        """运行主循环"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ShortcutApp()
    app.run()

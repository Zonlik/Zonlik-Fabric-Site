import tkinter as tk
from tkinter import messagebox
import os
import subprocess

class AutostartTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_info, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        disable_btn = tk.Button(btn_frame, text="🚫 Отключить выбранное", command=self.disable_selected, bg=app.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        disable_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.update_info()
    
    def update_info(self):
        info = []
        info.append("=" * 60)
        info.append("АВТОЗАГРУЗКА ПРОГРАММ")
        info.append("=" * 60)
        
        autostart_dir = os.path.expanduser("~/.config/autostart")
        
        info.append(f"\n📁 Пользовательские:")
        info.append("-" * 40)
        
        if os.path.exists(autostart_dir):
            for f in sorted(os.listdir(autostart_dir)):
                if f.endswith('.desktop'):
                    filepath = os.path.join(autostart_dir, f)
                    try:
                        with open(filepath, 'r') as file:
                            for line in file:
                                if 'Name=' in line and not line.startswith('#'):
                                    app_name = line.split('=')[1].strip()
                                    info.append(f"  ✅ {app_name} ({f})")
                                    break
                    except:
                        info.append(f"  ✅ {f}")
        else:
            info.append("  Нет программ")
        
        info.append(f"\n📁 Системные (/etc/xdg/autostart):")
        info.append("-" * 40)
        
        system_dir = "/etc/xdg/autostart"
        if os.path.exists(system_dir):
            for f in sorted(os.listdir(system_dir)):
                if f.endswith('.desktop'):
                    info.append(f"  📌 {f}")
        
        info.append("\n" + "=" * 60)
        info.append("CRON ЗАДАЧИ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.split('\n')[:10]:
                    if line.strip() and not line.startswith('#'):
                        info.append(f"  {line[:70]}")
            else:
                info.append("  Нет cron задач")
        except:
            info.append("  Нет cron задач")
        
        info.append("\n💡 Для отключения:")
        info.append("  • Нажмите 'Отключить выбранное'")
        info.append("  • Или переместите .desktop файл")
        info.append("    в папку с расширением .disabled")
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))
    
    def disable_selected(self):
        autostart_dir = os.path.expanduser("~/.config/autostart")
        
        if not os.path.exists(autostart_dir):
            messagebox.showinfo("Инфо", "Нет программ в автозагрузке")
            return
        
        win = tk.Toplevel(self.app.root)
        win.title("Отключение автозагрузки")
        win.geometry("550x400")
        win.configure(bg=self.app.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.app.graph_bg, fg=self.app.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "ПРОГРАММЫ В АВТОЗАГРУЗКЕ\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        for f in sorted(os.listdir(autostart_dir)):
            if f.endswith('.desktop'):
                filepath = os.path.join(autostart_dir, f)
                try:
                    with open(filepath, 'r') as file:
                        for line in file:
                            if 'Name=' in line and not line.startswith('#'):
                                app_name = line.split('=')[1].strip()
                                text_widget.insert(tk.END, f"  {app_name} — {f}\n")
                                break
                except:
                    text_widget.insert(tk.END, f"  {f}\n")
        
        text_widget.insert(tk.END, "\n" + "=" * 50 + "\n")
        text_widget.insert(tk.END, f"Отключить: переименуйте файл\nв {autostart_dir}\n")
        text_widget.insert(tk.END, "mv имя.desktop имя.desktop.disabled\n")
        text_widget.insert(tk.END, "\nЗатем нажмите 'Обновить'")
        
        text_widget.config(state=tk.DISABLED)

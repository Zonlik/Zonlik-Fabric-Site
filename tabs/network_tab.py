import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

class NetworkTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_info, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        kill_btn = tk.Button(btn_frame, text="🔪 Закрыть соединение", command=self.kill_connection, bg=app.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        kill_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 9), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.update_info()
        self.update_loop()
    
    def update_loop(self):
        if self.app.running:
            self.update_info()
            self.frame.after(5000, self.update_loop)
    
    def update_info(self):
        info = []
        info.append("=" * 60)
        info.append("АКТИВНЫЕ СЕТЕВЫЕ СОЕДИНЕНИЯ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['ss', '-tunap'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            info.append(f"\n{'State':10} {'Recv-Q':6} {'Send-Q':6} {'Local':35} {'Peer':35} {'Process'}")
            info.append("-" * 110)
            for line in lines[1:40]:
                if line.strip():
                    info.append(line[:110])
        except:
            info.append("Ошибка получения соединений")
        
        info.append("\n" + "=" * 60)
        info.append("ОТКРЫТЫЕ ПОРТЫ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
            for line in result.stdout.split('\n')[1:10]:
                if line.strip():
                    info.append(line[:80])
        except:
            pass
        
        info.append("\n" + "=" * 60)
        info.append("ПОДОЗРИТЕЛЬНЫЕ СОЕДИНЕНИЯ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['ss', '-tunap'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'ESTAB' in line and not ('127.0.0' in line or '::1' in line):
                    info.append(f"⚠️ {line[:80]}")
        except:
            pass
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))
    
    def kill_connection(self):
        win = tk.Toplevel(self.app.root)
        win.title("Закрыть соединение")
        win.geometry("500x300")
        win.configure(bg=self.app.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('Courier', 9), bg=self.app.graph_bg, fg=self.app.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            result = subprocess.run(['ss', '-tunap'], capture_output=True, text=True)
            text_widget.insert(tk.END, "Активные соединения:\n\n")
            for line in result.stdout.split('\n')[:30]:
                if 'ESTAB' in line:
                    text_widget.insert(tk.END, f"{line}\n")
            
            text_widget.insert(tk.END, "\n" + "=" * 50 + "\n")
            text_widget.insert(tk.END, "Для закрытия:\n")
            text_widget.insert(tk.END, "  sudo kill -9 PID\n")
        except Exception as e:
            text_widget.insert(tk.END, f"Ошибка: {e}\n")
        
        text_widget.config(state=tk.DISABLED)

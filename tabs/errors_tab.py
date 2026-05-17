import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

class ErrorsTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        self.notebook = parent
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_info, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Очистить логи", command=self.clear_logs, bg=app.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 9), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.update_info()
    
    def update_info(self):
        info = []
        info.append("=" * 60)
        info.append("СИСТЕМНЫЕ ОШИБКИ И СБОИ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['dmesg', '-T', '|', 'grep', '-i', 'error'], capture_output=True, text=True, shell=True)
            errors = [line for line in result.stdout.split('\n') if line.strip()]
            if errors:
                info.append(f"\n🔴 ОШИБКИ ЯДРА: {len(errors)}")
                info.append("-" * 40)
                for err in errors[-10:]:
                    info.append(f"  {err[:100]}")
            else:
                info.append("\n✅ Ошибок ядра не найдено")
            
            result = subprocess.run(['dmesg', '-T', '|', 'grep', '-i', 'segfault'], capture_output=True, text=True, shell=True)
            segfaults = [line for line in result.stdout.split('\n') if line.strip()]
            if segfaults:
                info.append(f"\n💥 СБОИ ПРИЛОЖЕНИЙ: {len(segfaults)}")
                info.append("-" * 40)
                for err in segfaults[-5:]:
                    info.append(f"  {err[:100]}")
            
            result = subprocess.run(['journalctl', '-p', '3', '-n', '30', '--no-pager'], capture_output=True, text=True)
            info.append("\n" + "=" * 60)
            info.append("ПОСЛЕДНИЕ ОШИБКИ (journalctl)")
            info.append("=" * 60)
            for line in result.stdout.split('\n')[:20]:
                if line.strip():
                    info.append(f"  {line[:120]}")
        except Exception as e:
            info.append(f"Ошибка: {e}")
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))
    
    def clear_logs(self):
        result = messagebox.askyesno("Очистка логов", "Очистить журнал ошибок?\n⚠️ Требует пароль!")
        if result:
            def clear():
                try:
                    subprocess.run(['pkexec', 'journalctl', '--rotate'], capture_output=True)
                    subprocess.run(['pkexec', 'journalctl', '--vacuum-time=1s'], capture_output=True)
                    self.app.show_notification("Zonlik", "Логи очищены")
                    self.update_info()
                except Exception as e:
                    self.app.show_notification("Zonlik", f"Ошибка: {e}")
            threading.Thread(target=clear, daemon=True).start()

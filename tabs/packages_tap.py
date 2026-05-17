import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

class PackagesTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_info, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = tk.Button(btn_frame, text="🗑️ Удалить пакет", command=self.remove_package, bg='#f38ba8', fg='white', padx=10, pady=4, relief='flat')
        remove_btn.pack(side=tk.LEFT, padx=5)
        
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
        info.append("УСТАНОВЛЕННЫЕ ПАКЕТЫ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            info.append(f"\nВсего пакетов: {len([l for l in lines if l.startswith('ii')])}")
            info.append("\nПОСЛЕДНИЕ УСТАНОВЛЕННЫЕ:")
            info.append("-" * 40)
            
            count = 0
            for line in reversed(lines):
                if line.startswith('ii') and count < 20:
                    parts = line.split()
                    if len(parts) >= 2:
                        info.append(f"  {parts[1]}")
                        count += 1
        except Exception as e:
            info.append(f"Ошибка: {e}")
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))
    
    def remove_package(self):
        win = tk.Toplevel(self.app.root)
        win.title("Удаление пакета")
        win.geometry("500x300")
        win.configure(bg=self.app.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('Courier', 9), bg=self.app.graph_bg, fg=self.app.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "Введите имя пакета для удаления:\n\n")
        
        entry = tk.Entry(win, font=('Courier', 10), bg=self.app.graph_bg, fg=self.app.fg)
        entry.pack(pady=5, padx=10, fill=tk.X)
        
        def do_remove():
            pkg = entry.get().strip()
            if not pkg:
                return
            result = messagebox.askyesno("Удаление", f"Удалить пакет {pkg}?\n⚠️ Требует пароль!")
            if result:
                def remove():
                    try:
                        subprocess.run(['pkexec', 'apt', 'remove', '-y', pkg], capture_output=True)
                        self.app.root.after(0, lambda: self.app.show_notification("Zonlik", f"Пакет {pkg} удалён"))
                        self.app.root.after(0, self.update_info)
                        win.destroy()
                    except Exception as e:
                        self.app.root.after(0, lambda: self.app.show_notification("Zonlik", f"Ошибка: {e}"))
                threading.Thread(target=remove, daemon=True).start()
        
        btn_frame = tk.Frame(win, bg=self.app.bg)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Удалить", command=do_remove, bg='#f38ba8', fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=win.destroy, bg=self.app.secondary, fg='#1a1b26', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        text_widget.config(state=tk.DISABLED)

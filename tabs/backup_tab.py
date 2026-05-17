import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os
import datetime
import shutil

class BackupTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        backup_btn = tk.Button(btn_frame, text="💾 Создать бэкап", command=self.create_backup, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        backup_btn.pack(side=tk.LEFT, padx=5)
        
        restore_btn = tk.Button(btn_frame, text="🔄 Восстановить", command=self.restore_backup, bg=app.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        restore_btn.pack(side=tk.LEFT, padx=5)
        
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
        info.append("РЕЗЕРВНОЕ КОПИРОВАНИЕ")
        info.append("=" * 60)
        
        backup_dir = os.path.expanduser("~/zonlik_backups")
        if os.path.exists(backup_dir):
            info.append(f"\n📁 Папка бэкапов: {backup_dir}")
            backups = os.listdir(backup_dir)
            info.append(f"Количество бэкапов: {len(backups)}")
            info.append("\nПОСЛЕДНИЕ БЭКАПЫ:")
            info.append("-" * 40)
            for b in sorted(backups, reverse=True)[:10]:
                info.append(f"  {b}")
        else:
            info.append("\n📁 Бэкапов пока нет")
            info.append("Нажмите 'Создать бэкап'")
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))
    
    def create_backup(self):
        backup_dir = os.path.expanduser("~/zonlik_backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        self.app.show_notification("Zonlik", "Создание бэкапа...")
        
        def backup():
            try:
                # Копируем настройки программы
                if os.path.exists(self.app.settings_file):
                    shutil.copy(self.app.settings_file, backup_path)
                
                # Копируем историю батареи
                history_file = os.path.expanduser("~/.zonlik_battery_history.json")
                if os.path.exists(history_file):
                    shutil.copy(history_file, backup_path)
                
                # Копируем .desktop файл
                desktop_file = os.path.expanduser("~/.local/share/applications/zonlik-monitor.desktop")
                if os.path.exists(desktop_file):
                    shutil.copy(desktop_file, backup_path)
                
                self.app.root.after(0, lambda: self.app.show_notification("Zonlik", f"Бэкап создан: {backup_path}"))
                self.app.root.after(0, self.update_info)
            except Exception as e:
                self.app.root.after(0, lambda: self.app.show_notification("Zonlik", f"Ошибка: {e}"))
        
        threading.Thread(target=backup, daemon=True).start()
    
    def restore_backup(self):
        backup_dir = os.path.expanduser("~/zonlik_backups")
        if not os.path.exists(backup_dir):
            messagebox.showinfo("Инфо", "Нет бэкапов")
            return
        
        win = tk.Toplevel(self.app.root)
        win.title("Восстановление из бэкапа")
        win.geometry("500x400")
        win.configure(bg=self.app.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.app.graph_bg, fg=self.app.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "ВЫБЕРИТЕ БЭКАП ДЛЯ ВОССТАНОВЛЕНИЯ\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        backups = sorted(os.listdir(backup_dir), reverse=True)
        for b in backups:
            text_widget.insert(tk.END, f"  {b}\n")
        
        text_widget.insert(tk.END, "\n" + "=" * 50 + "\n")
        text_widget.insert(tk.END, "Введите имя бэкапа для восстановления:\n")
        
        entry = tk.Entry(win, font=('Courier', 10), bg=self.app.graph_bg, fg=self.app.fg)
        entry.pack(pady=5, padx=10, fill=tk.X)
        
        def do_restore():
            backup_name = entry.get().strip()
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                messagebox.showerror("Ошибка", "Бэкап не найден")
                return
            
            result = messagebox.askyesno("Восстановление", f"Восстановить из {backup_name}?")
            if result:
                def restore():
                    try:
                        for file in os.listdir(backup_path):
                            src = os.path.join(backup_path, file)
                            if file == 'zonlik_monitor.desktop':
                                dst = os.path.expanduser("~/.local/share/applications/zonlik-monitor.desktop")
                            elif file == '.zonlik_settings.json':
                                dst = self.app.settings_file
                            elif file == '.zonlik_battery_history.json':
                                dst = os.path.expanduser("~/.zonlik_battery_history.json")
                            else:
                                continue
                            shutil.copy(src, dst)
                        self.app.root.after(0, lambda: self.app.show_notification("Zonlik", "Восстановление завершено"))
                        self.app.root.after(0, win.destroy)
                    except Exception as e:
                        self.app.root.after(0, lambda: self.app.show_notification("Zonlik", f"Ошибка: {e}"))
                
                threading.Thread(target=restore, daemon=True).start()
        
        btn_frame = tk.Frame(win, bg=self.app.bg)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Восстановить", command=do_restore, bg=self.app.accent, fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=win.destroy, bg=self.app.secondary, fg='#1a1b26', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        text_widget.config(state=tk.DISABLED)

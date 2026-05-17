import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading

class CacheTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_info, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clean_btn = tk.Button(btn_frame, text="🧹 Очистить всё", command=self.clean_all, bg='#f38ba8', fg='white', padx=10, pady=4, relief='flat')
        clean_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.update_info()
    
    def get_folder_size(self, path):
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_folder_size(entry.path)
        except:
            pass
        return total / (1024*1024)
    
    def update_info(self):
        info = []
        info.append("=" * 60)
        info.append("КЭШ И ВРЕМЕННЫЕ ФАЙЛЫ")
        info.append("=" * 60)
        
        caches = [
            ("~/.cache", os.path.expanduser("~/.cache")),
            ("/tmp", "/tmp"),
            ("/var/cache", "/var/cache"),
            ("~/.thumbnails", os.path.expanduser("~/.cache/thumbnails")),
        ]
        
        total_size = 0
        for name, path in caches:
            if os.path.exists(path):
                size = self.get_folder_size(path)
                total_size += size
                if size > 0.1:
                    info.append(f"  {name}: {size:.1f} MB")
                else:
                    info.append(f"  {name}: {size*1024:.0f} KB")
            else:
                info.append(f"  {name}: не найден")
        
        info.append(f"\n📊 ОБЩИЙ РАЗМЕР: {total_size:.1f} MB")
        
        if total_size > 1000:
            info.append("⚠️ Кэш > 1 ГБ! Рекомендуется очистка.")
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))
    
    def clean_all(self):
        result = messagebox.askyesno("Очистка кэша", 
            "Очистить все временные файлы и кэш?\n"
            "Будут удалены:\n"
            "• ~/.cache\n"
            "• /tmp (ваши файлы)\n"
            "• Миниатюры\n\n"
            "Продолжить?")
        
        if not result:
            return
        
        self.app.show_notification("Zonlik", "Очистка кэша...")
        
        def clean():
            try:
                subprocess.run(['rm', '-rf', os.path.expanduser("~/.cache/*")], capture_output=True)
                subprocess.run(['rm', '-rf', '/tmp/*'], capture_output=True)
                subprocess.run(['rm', '-rf', os.path.expanduser("~/.cache/thumbnails/*")], capture_output=True)
                self.app.root.after(0, lambda: self.app.show_notification("Zonlik", "Кэш очищен"))
                self.app.root.after(0, self.update_info)
            except Exception as e:
                self.app.root.after(0, lambda: self.app.show_notification("Zonlik", f"Ошибка: {e}"))
        
        threading.Thread(target=clean, daemon=True).start()

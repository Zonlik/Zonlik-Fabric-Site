import tkinter as tk
from tkinter import messagebox, filedialog
import os
import hashlib
import threading
from collections import defaultdict

class DuplicatesTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        scan_btn = tk.Button(btn_frame, text="🔍 Сканировать папку", command=self.scan_folder, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        scan_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 9), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.duplicates = []
    
    def scan_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку для сканирования")
        if not folder:
            return
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, f"Сканирование {folder}...\n\n")
        self.frame.update()
        
        def scan():
            files_by_hash = defaultdict(list)
            total = 0
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'rb') as f:
                            file_hash = hashlib.md5(f.read(1024*1024)).hexdigest()
                        files_by_hash[file_hash].append(filepath)
                        total += 1
                        if total % 100 == 0:
                            self.app.root.after(0, lambda: self.text.insert(tk.END, f"  Обработано {total} файлов...\n"))
                    except:
                        pass
            
            self.duplicates = []
            self.app.root.after(0, self.text.delete, 1.0, tk.END)
            self.app.root.after(0, self.text.insert, tk.END, "ДУБЛИКАТЫ ФАЙЛОВ\n")
            self.app.root.after(0, self.text.insert, tk.END, "=" * 50 + "\n\n")
            
            for file_hash, files in files_by_hash.items():
                if len(files) > 1:
                    self.duplicates.append(files)
                    self.app.root.after(0, self.text.insert, tk.END, f"Найдено {len(files)} дубликатов:\n")
                    for f in files:
                        self.app.root.after(0, self.text.insert, tk.END, f"  {f}\n")
                    self.app.root.after(0, self.text.insert, tk.END, "\n")
            
            if not self.duplicates:
                self.app.root.after(0, self.text.insert, tk.END, "Дубликатов не найдено\n")
        
        threading.Thread(target=scan, daemon=True).start()

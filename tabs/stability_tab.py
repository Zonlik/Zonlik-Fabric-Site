import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time
import math

class StabilityTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        cpu_btn = tk.Button(btn_frame, text="🧠 Тест CPU", command=self.test_cpu, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        cpu_btn.pack(side=tk.LEFT, padx=5)
        
        mem_btn = tk.Button(btn_frame, text="💾 Тест RAM", command=self.test_memory, bg=app.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        mem_btn.pack(side=tk.LEFT, padx=5)
        
        disk_btn = tk.Button(btn_frame, text="💿 Тест диска", command=self.test_disk, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        disk_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 9), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.text.insert(tk.END, "Нажмите кнопку для запуска теста\n")
    
    def test_cpu(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "Тест CPU запущен...\n\n")
        self.frame.update()
        
        start = time.time()
        pi = 0
        for i in range(1, 2000000, 4):
            pi += 4/i - 4/(i+2)
            if i % 100000 == 0:
                self.text.insert(tk.END, f"  Прогресс: {i/20000:.1f}%\n")
                self.frame.update()
        
        elapsed = time.time() - start
        self.text.insert(tk.END, f"\n✅ Тест CPU завершён за {elapsed:.2f} сек\n")
    
    def test_memory(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "Тест RAM запущен...\n\n")
        self.frame.update()
        
        try:
            result = subprocess.run(['stress-ng', '--vm', '1', '--vm-bytes', '80%', '--timeout', '10s'], capture_output=True, text=True)
            self.text.insert(tk.END, result.stderr if result.stderr else result.stdout)
            self.text.insert(tk.END, "\n✅ Тест RAM завершён\n")
        except:
            self.text.insert(tk.END, "❌ stress-ng не установлен\n")
            self.text.insert(tk.END, "Установите: sudo apt install stress-ng\n")
    
    def test_disk(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "Тест диска запущен...\n\n")
        self.frame.update()
        
        try:
            result = subprocess.run(['dd', 'if=/dev/zero', 'of=/tmp/test', 'bs=1M', 'count=200', 'conv=fdatasync'], capture_output=True, text=True)
            self.text.insert(tk.END, result.stderr)
            self.text.insert(tk.END, "\n✅ Тест диска завершён\n")
            subprocess.run(['rm', '/tmp/test'])
        except Exception as e:
            self.text.insert(tk.END, f"Ошибка: {e}\n")

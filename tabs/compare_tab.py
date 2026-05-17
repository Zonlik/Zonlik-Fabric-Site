import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time
import math
import json
import os

class CompareTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        self.results_file = os.path.expanduser("~/.zonlik_benchmark.json")
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        run_btn = tk.Button(btn_frame, text="🚀 Запустить тест", command=self.run_benchmark, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        run_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 9), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.load_results()
    
    def load_results(self):
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    self.results = json.load(f)
            except:
                self.results = []
        else:
            self.results = []
        self.show_results()
    
    def save_results(self):
        with open(self.results_file, 'w') as f:
            json.dump(self.results[-10:], f)
    
    def show_results(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "ИСТОРИЯ ТЕСТОВ\n")
        self.text.insert(tk.END, "=" * 50 + "\n\n")
        
        if not self.results:
            self.text.insert(tk.END, "Тестов пока нет. Нажмите 'Запустить тест'\n")
            return
        
        for r in self.results:
            self.text.insert(tk.END, f"{r['date']}\n")
            self.text.insert(tk.END, f"  CPU: {r['cpu_score']:.2f} сек\n")
            self.text.insert(tk.END, f"  RAM: {r['ram_score']:.2f} сек\n")
            self.text.insert(tk.END, f"  Диск: {r['disk_score']:.2f} MB/s\n")
            self.text.insert(tk.END, "-" * 30 + "\n")
    
    def run_benchmark(self):
        self.text.insert(tk.END, "\nЗапуск теста...\n")
        self.frame.update()
        
        def benchmark():
            import datetime
            
            start = time.time()
            pi = 0
            for i in range(1, 1000000, 4):
                pi += 4/i - 4/(i+2)
            cpu_score = time.time() - start
            
            start = time.time()
            arr = [i for i in range(1000000)]
            ram_score = time.time() - start
            
            result = subprocess.run(['dd', 'if=/dev/zero', 'of=/tmp/test', 'bs=1M', 'count=100', 'conv=fdatasync'], capture_output=True, text=True)
            disk_score = 0
            if 'MB/s' in result.stderr:
                try:
                    disk_score = float(result.stderr.split('MB/s')[0].split(',')[-1].strip())
                except:
                    disk_score = 0
            subprocess.run(['rm', '/tmp/test'])
            
            self.results.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'cpu_score': cpu_score,
                'ram_score': ram_score,
                'disk_score': disk_score
            })
            self.save_results()
            
            self.app.root.after(0, self.show_results)
            self.app.root.after(0, lambda: self.app.show_notification("Zonlik", "Тест завершён"))
        
        threading.Thread(target=benchmark, daemon=True).start()

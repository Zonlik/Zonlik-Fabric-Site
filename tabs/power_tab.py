import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import psutil

class PowerTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=app.bg)
        
        btn_frame = tk.Frame(self.frame, bg=app.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_info, bg=app.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(self.frame, bg=app.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=app.graph_bg, fg=app.fg, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)
        
        self.update_info()
        self.update_loop()
    
    def update_loop(self):
        if self.app.running:
            self.update_info()
            self.frame.after(3000, self.update_loop)
    
    def update_info(self):
        info = []
        info.append("=" * 60)
        info.append("ЭНЕРГОПОТРЕБЛЕНИЕ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['sensors'], capture_output=True, text=True)
            info.append("\n🔋 CPU:")
            for line in result.stdout.split('\n'):
                if 'Power' in line or 'power' in line:
                    info.append(f"  {line.strip()}")
        except:
            pass
        
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=power.draw,power.limit', '--format=csv,noheader'], capture_output=True, text=True)
            if result.returncode == 0:
                info.append("\n🎮 GPU:")
                info.append(f"  {result.stdout.strip()}")
        except:
            pass
        
        info.append("\n📊 СИСТЕМА:")
        battery = psutil.sensors_battery()
        if battery:
            info.append(f"  Заряд батареи: {battery.percent}%")
            if battery.secsleft > 0:
                info.append(f"  Время до разряда: {battery.secsleft // 60} мин")
        
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "\n".join(info))

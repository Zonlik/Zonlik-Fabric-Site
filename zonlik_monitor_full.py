#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
import json
import subprocess
import threading
import time
from collections import deque

# ASCII Art
ZONLIK_ASCII = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ███████╗ ██████╗ ███╗   ██╗██╗     ██╗██╗  ██╗                           ║
║     ╚══███╔╝██╔═══██╗████╗  ██║██║     ██║██║ ██╔╝   Create by: Barinov      ║
║       ███╔╝ ██║   ██║██╔██╗ ██║██║     ██║█████╔╝               Kirill       ║
║      ███╔╝  ██║   ██║██║╚██╗██║██║     ██║██╔═██╗               Sergeevich   ║
║     ███████╗╚██████╔╝██║ ╚████║███████╗██║██║  ██╗                           ║
║     ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚═╝  ╚═╝                           ║
║                                                                              ║
║   ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗                ║
║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝                ║
║   █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝                 ║
║   ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝                  ║
║   ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║                   ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝                   ║
║                                                                              ║
║                    ZONLIK FACTORY PROGRAMM v1.44                             ║
║                "Monitor your system, control your hardware"                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

class ZonlikMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Zonlik Monitor")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        self.root.configure(bg='#1a1b26')
        
        self.settings_file = os.path.expanduser("~/.zonlik_settings.json")
        self.load_settings()
        
        self.cpu_history = deque(maxlen=60)
        self.ram_history = deque(maxlen=60)
        self.gpu_history = deque(maxlen=60)
        self.disk_read_history = deque(maxlen=60)
        self.disk_write_history = deque(maxlen=60)
        self.net_down_history = deque(maxlen=60)
        self.net_up_history = deque(maxlen=60)
        self.running = True
        
        self.current_theme = self.settings.get("theme", "dark_matter")
        self.graph_style = self.settings.get("graph_style", "fancy")
        self.apply_theme()
        
        self.notifications_enabled = self.settings.get("notifications", True)
        
        self.setup_ui()
        
        self.root.after(1000, self.update_stats)
        self.root.after(3000, self.update_process_list)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {}
        else:
            self.settings = {}
        self.settings.setdefault("theme", "dark_matter")
        self.settings.setdefault("graph_style", "fancy")
        self.settings.setdefault("show_cpu_graph", True)
        self.settings.setdefault("show_ram_graph", True)
        self.settings.setdefault("show_gpu_graph", False)
        self.settings.setdefault("show_disk_graph", True)
        self.settings.setdefault("show_net_graph", True)
        self.settings.setdefault("update_interval", 1.0)
        self.settings.setdefault("notifications", True)
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
    
    def apply_theme(self):
        themes = {
            "dark_matter": {"bg": "#1a1b26", "fg": "#c0caf5", "accent": "#bb86fc", "secondary": "#03dac6", "graph_bg": "#24273a"},
            "cyberpunk": {"bg": "#0a0a0f", "fg": "#00ffcc", "accent": "#ff00ff", "secondary": "#ffcc00", "graph_bg": "#0a0a1a"},
            "matrix": {"bg": "#0a0f0a", "fg": "#00ff00", "accent": "#33ff33", "secondary": "#88ff88", "graph_bg": "#0a1a0a"},
            "sunset": {"bg": "#1a0f0f", "fg": "#ffcc99", "accent": "#ff6600", "secondary": "#ffaa44", "graph_bg": "#2a1a1a"},
            "ocean": {"bg": "#0a1a2a", "fg": "#c0e0ff", "accent": "#3399ff", "secondary": "#66ccff", "graph_bg": "#0a2a3a"},
            "forest": {"bg": "#0a1a0a", "fg": "#ccffcc", "accent": "#33cc33", "secondary": "#88dd88", "graph_bg": "#0a2a0a"},
            "royal": {"bg": "#1a0a2a", "fg": "#e0ccff", "accent": "#aa66ff", "secondary": "#cc88ff", "graph_bg": "#2a0a3a"},
            "cherry": {"bg": "#1a0a1a", "fg": "#ffccdd", "accent": "#ff66aa", "secondary": "#ff99cc", "graph_bg": "#2a0a2a"}
        }
        theme = themes.get(self.current_theme, themes["dark_matter"])
        self.bg = theme["bg"]
        self.fg = theme["fg"]
        self.accent = theme["accent"]
        self.secondary = theme["secondary"]
        self.graph_bg = theme["graph_bg"]
        self.root.configure(bg=self.bg)
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.setup_monitor_tab()
        self.setup_processes_tab()
        self.setup_cpu_tab()
        self.setup_ram_tab()
        self.setup_gpu_tab()
        self.setup_battery_tab()
        self.setup_disks_tab()
        self.setup_usb_tab()
        self.setup_motherboard_tab()
        self.setup_system_tab()
        self.setup_settings_tab()
        self.setup_help_tab()
        
        self.status_label = tk.Label(main_frame, text="✅ Мониторинг активен", fg='#a6e3a1', bg=self.bg, font=('SegoeUI', 9))
        self.status_label.pack(pady=5)
    
    def setup_monitor_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Мониторинг")
        
        # Левая часть - графики
        canvas_frame = tk.Frame(frame, bg=self.bg)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.graphs = []
        self.graph_vars = {}
        
        # CPU
        cpu_frame = tk.Frame(canvas_frame, bg=self.bg)
        cpu_frame.pack(fill=tk.X, pady=5)
        
        self.graph_vars['cpu'] = tk.BooleanVar(value=self.settings.get("show_cpu_graph", True))
        cpu_btn = tk.Checkbutton(cpu_frame, text="CPU", variable=self.graph_vars['cpu'], bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.toggle_cpu_graph)
        cpu_btn.pack(side=tk.LEFT)
        
        self.canvas_cpu = tk.Canvas(cpu_frame, height=80, bg=self.graph_bg, highlightthickness=1)
        self.canvas_cpu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.graphs.append(('cpu', self.canvas_cpu))
        
        # RAM
        ram_frame = tk.Frame(canvas_frame, bg=self.bg)
        ram_frame.pack(fill=tk.X, pady=5)
        
        self.graph_vars['ram'] = tk.BooleanVar(value=self.settings.get("show_ram_graph", True))
        ram_btn = tk.Checkbutton(ram_frame, text="RAM", variable=self.graph_vars['ram'], bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.toggle_ram_graph)
        ram_btn.pack(side=tk.LEFT)
        
        self.canvas_ram = tk.Canvas(ram_frame, height=80, bg=self.graph_bg, highlightthickness=1)
        self.canvas_ram.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.graphs.append(('ram', self.canvas_ram))
        
        # GPU
        gpu_frame = tk.Frame(canvas_frame, bg=self.bg)
        gpu_frame.pack(fill=tk.X, pady=5)
        
        self.graph_vars['gpu'] = tk.BooleanVar(value=self.settings.get("show_gpu_graph", False))
        gpu_btn = tk.Checkbutton(gpu_frame, text="GPU", variable=self.graph_vars['gpu'], bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.toggle_gpu_graph)
        gpu_btn.pack(side=tk.LEFT)
        
        self.canvas_gpu = tk.Canvas(gpu_frame, height=80, bg=self.graph_bg, highlightthickness=1)
        self.canvas_gpu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.graphs.append(('gpu', self.canvas_gpu))
        
        # Диск
        disk_frame = tk.Frame(canvas_frame, bg=self.bg)
        disk_frame.pack(fill=tk.X, pady=5)
        
        self.graph_vars['disk'] = tk.BooleanVar(value=self.settings.get("show_disk_graph", True))
        disk_btn = tk.Checkbutton(disk_frame, text="DISK", variable=self.graph_vars['disk'], bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.toggle_disk_graph)
        disk_btn.pack(side=tk.LEFT)
        
        self.canvas_disk = tk.Canvas(disk_frame, height=80, bg=self.graph_bg, highlightthickness=1)
        self.canvas_disk.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.graphs.append(('disk', self.canvas_disk))
        
        # Сеть
        net_frame = tk.Frame(canvas_frame, bg=self.bg)
        net_frame.pack(fill=tk.X, pady=5)
        
        self.graph_vars['net'] = tk.BooleanVar(value=self.settings.get("show_net_graph", True))
        net_btn = tk.Checkbutton(net_frame, text="INTERNET", variable=self.graph_vars['net'], bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.toggle_net_graph)
        net_btn.pack(side=tk.LEFT)
        
        self.canvas_net = tk.Canvas(net_frame, height=80, bg=self.graph_bg, highlightthickness=1)
        self.canvas_net.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.graphs.append(('net', self.canvas_net))
        
        # Правая часть - текущие показатели
        stats_frame = tk.Frame(frame, bg=self.bg, width=200)
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        stats_frame.pack_propagate(False)
        
        tk.Label(stats_frame, text="ТЕКУЩИЕ ПОКАЗАТЕЛИ", font=('SegoeUI', 10, 'bold'), fg=self.accent, bg=self.bg).pack(pady=5)
        
        self.cpu_val = tk.Label(stats_frame, text="CPU: --%", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.cpu_val.pack(anchor='w', pady=2)
        
        self.ram_val = tk.Label(stats_frame, text="RAM: --%", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.ram_val.pack(anchor='w', pady=2)
        
        self.gpu_val = tk.Label(stats_frame, text="GPU: --%", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.gpu_val.pack(anchor='w', pady=2)
        
        self.disk_val = tk.Label(stats_frame, text="DISK: -- MB/s", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.disk_val.pack(anchor='w', pady=2)
        
        self.net_val = tk.Label(stats_frame, text="INTERNET: ↓-- ↑--", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.net_val.pack(anchor='w', pady=2)
        
        self.cpu_temp_val = tk.Label(stats_frame, text="🌡️ CPU: --°C", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.cpu_temp_val.pack(anchor='w', pady=2)
        
        self.gpu_temp_val = tk.Label(stats_frame, text="🌡️ GPU: --°C", font=('SegoeUI', 11), fg=self.fg, bg=self.bg)
        self.gpu_temp_val.pack(anchor='w', pady=2)
        
        self.refresh_graphs()

    def toggle_cpu_graph(self):
        self.settings["show_cpu_graph"] = self.graph_vars['cpu'].get()
        self.save_settings()
        if self.graph_vars['cpu'].get():
            self.canvas_cpu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.canvas_cpu.pack_forget()
    
    def toggle_ram_graph(self):
        self.settings["show_ram_graph"] = self.graph_vars['ram'].get()
        self.save_settings()
        if self.graph_vars['ram'].get():
            self.canvas_ram.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.canvas_ram.pack_forget()
    
    def toggle_gpu_graph(self):
        self.settings["show_gpu_graph"] = self.graph_vars['gpu'].get()
        self.save_settings()
        if self.graph_vars['gpu'].get():
            self.canvas_gpu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.canvas_gpu.pack_forget()
    
    def toggle_disk_graph(self):
        self.settings["show_disk_graph"] = self.graph_vars['disk'].get()
        self.save_settings()
        if self.graph_vars['disk'].get():
            self.canvas_disk.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.canvas_disk.pack_forget()
    
    def toggle_net_graph(self):
        self.settings["show_net_graph"] = self.graph_vars['net'].get()
        self.save_settings()
        if self.graph_vars['net'].get():
            self.canvas_net.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.canvas_net.pack_forget()
    
    def setup_processes_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Процессы")
        
        columns = ('pid', 'name', 'cpu', 'memory')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        self.tree.heading('pid', text='PID')
        self.tree.heading('name', text='Имя')
        self.tree.heading('cpu', text='CPU %')
        self.tree.heading('memory', text='RAM %')
        self.tree.column('pid', width=70)
        self.tree.column('name', width=350)
        self.tree.column('cpu', width=80)
        self.tree.column('memory', width=80)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        refresh_btn = tk.Button(btn_frame, text="Обновить", command=self.update_process_list, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        kill_btn = tk.Button(btn_frame, text="⚡ Убить выбранный", command=self.kill_selected_process, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        kill_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_cpu_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Процессор")
        
        text_frame = tk.Frame(frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cpu_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.cpu_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.cpu_text.yview)
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5)
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_cpu_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack()
        
        self.update_cpu_info()
        self.update_cpu_loop()
    
    def update_cpu_loop(self):
        if self.running:
            self.update_cpu_info()
            self.root.after(10000, self.update_cpu_loop)
    
    def update_cpu_info(self):
        info = []
        info.append("=" * 60)
        info.append("ИНФОРМАЦИЯ О ПРОЦЕССОРЕ")
        info.append("=" * 60)
        
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        cpu_model = line.split(':')[1].strip()
                        info.append(f"Модель: {cpu_model}")
                        break
            
            import platform
            arch = platform.machine()
            info.append(f"Архитектура: {arch}")
            
            cores = 0
            threads = 0
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'cpu cores' in line:
                        cores = line.split(':')[1].strip()
                    if 'processor' in line:
                        threads += 1
            info.append(f"Физических ядер: {cores}")
            info.append(f"Логических ядер (потоков): {threads}")
            
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'cache size' in line:
                        info.append(f"L2 кэш: {line.split(':')[1].strip()}")
                        break
            
            freq = psutil.cpu_freq()
            if freq:
                if freq.current < 500:
                    info.append(f"⚠️ psutil показал ошибочную частоту: {freq.current:.0f} МГц")
                    info.append(f"Мин. частота: {freq.min:.0f} МГц")
                    info.append(f"Макс. частота: {freq.max:.0f} МГц")
                else:
                    info.append(f"Текущая частота: {freq.current:.0f} МГц")
                    info.append(f"Мин. частота: {freq.min:.0f} МГц")
                    info.append(f"Макс. частота: {freq.max:.0f} МГц")
            else:
                info.append("Частота: данные недоступны")
            
            try:
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    temp = int(f.read().strip()) / 1000
                    info.append(f"Температура: {temp:.1f}°C")
            except:
                info.append("Температура: нет данных")
            
            cpu_percent = psutil.cpu_percent(interval=0.3)
            info.append(f"Общая загрузка: {cpu_percent}%")
            
            per_cpu = psutil.cpu_percent(interval=0.3, percpu=True)
            info.append(f"Загрузка по ядрам: {per_cpu}")
            
            info.append("")
            info.append("-" * 40)
            info.append("ПОДДЕРЖИВАЕМЫЕ ТЕХНОЛОГИИ")
            info.append("-" * 40)
            
            with open('/proc/cpuinfo', 'r') as f:
                flags_line = None
                for line in f:
                    if 'flags' in line:
                        flags_line = line
                        break
            
            if flags_line:
                flags = flags_line.split(':')[1].strip().split()
                
                techs = {
                    'sse': 'SSE',
                    'sse2': 'SSE2',
                    'sse3': 'SSE3',
                    'ssse3': 'SSSE3',
                    'sse4_1': 'SSE4.1',
                    'sse4_2': 'SSE4.2',
                    'avx': 'AVX',
                    'avx2': 'AVX2',
                    'avx512f': 'AVX-512F',
                    'aes': 'AES-NI',
                    'vmx': 'VT-x',
                    'svm': 'AMD-V',
                    'rdrand': 'RDRAND',
                    'fma': 'FMA3',
                    'bmi1': 'BMI1',
                    'bmi2': 'BMI2'
                }
                
                for flag, name in techs.items():
                    if flag in flags:
                        info.append(f"✅ {name}")
                
                info.append("")
                info.append("-" * 40)
                info.append("ВСЕ ФЛАГИ CPU")
                info.append("-" * 40)
                info.append(" ".join(flags))
            else:
                info.append("Флаги CPU не найдены")
            
            if 'temp' in locals() and temp > 85:
                info.append("⚠️ ВНИМАНИЕ: Процессор перегревается!")
            elif cpu_percent > 90:
                info.append("⚠️ Высокая загрузка процессора.")
            else:
                info.append("✅ Состояние нормальное")
            
        except Exception as e:
            info.append(f"Ошибка получения данных: {e}")
        
        self.cpu_text.delete(1.0, tk.END)
        self.cpu_text.insert(tk.END, "\n".join(info))
    
    def setup_ram_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Оперативная память")
        
        info_frame = tk.LabelFrame(frame, text="Информация о RAM", bg=self.bg, fg=self.fg, font=('SegoeUI', 11, 'bold'))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_frame = tk.Frame(info_frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ram_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.ram_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ram_text.yview)
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_ram_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        details_btn = tk.Button(btn_frame, text="🔓 Детали памяти (требует пароль)", command=self.show_ram_details, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        details_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_ram_info()
    
    def update_ram_info(self):
        info = []
        info.append("=" * 60)
        info.append("ОПЕРАТИВНАЯ ПАМЯТЬ (RAM)")
        info.append("=" * 60)
        
        mem = psutil.virtual_memory()
        info.append(f"Всего: {mem.total // (1024**3)} GB ({mem.total // (1024**2)} MB)")
        info.append(f"Используется: {mem.used // (1024**3)} GB ({mem.used // (1024**2)} MB)")
        info.append(f"Свободно: {mem.free // (1024**3)} GB ({mem.free // (1024**2)} MB)")
        info.append(f"Доступно: {mem.available // (1024**3)} GB ({mem.available // (1024**2)} MB)")
        info.append(f"Загрузка: {mem.percent}%")
        
        if hasattr(mem, 'cached'):
            info.append(f"Кэшировано: {mem.cached // (1024**3)} GB")
        if hasattr(mem, 'buffers'):
            info.append(f"Буферы: {mem.buffers // (1024**3)} GB")
        
        info.append("")
        info.append("=" * 60)
        info.append("SWAP (ПОДКАЧКА)")
        info.append("=" * 60)
        swap = psutil.swap_memory()
        info.append(f"Всего: {swap.total // (1024**3)} GB")
        info.append(f"Используется: {swap.used // (1024**3)} GB")
        info.append(f"Свободно: {swap.free // (1024**3)} GB")
        info.append(f"Загрузка: {swap.percent}%")
        
        info.append("")
        info.append("=" * 60)
        info.append("ДЕТАЛИ ПАМЯТИ")
        info.append("=" * 60)
        info.append("Для получения полной информации (частота, тип, производитель)")
        info.append("нажмите кнопку ниже и введите пароль.")
        
        self.ram_text.delete(1.0, tk.END)
        self.ram_text.insert(tk.END, "\n".join(info))
    
    def show_ram_details(self):
        try:
            result = subprocess.run(['pkexec', 'dmidecode', '-t', 'memory'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                win = tk.Toplevel(self.root)
                win.title("Детали оперативной памяти")
                win.geometry("700x500")
                win.configure(bg=self.bg)
                
                text_frame = tk.Frame(win, bg=self.bg)
                text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                scrollbar = tk.Scrollbar(text_frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.config(command=text_widget.yview)
                
                lines = result.stdout.split('\n')
                formatted = []
                for line in lines:
                    if 'Type:' in line and 'DRAM' in line:
                        formatted.append(f"🔹 {line.strip()}")
                    elif 'Speed:' in line:
                        formatted.append(f"⚡ {line.strip()}")
                    elif 'Manufacturer:' in line:
                        formatted.append(f"🏭 {line.strip()}")
                    elif 'Part Number:' in line:
                        formatted.append(f"📦 {line.strip()}")
                    elif 'Size:' in line and 'MB' in line:
                        formatted.append(f"💾 {line.strip()}")
                
                if formatted:
                    text_widget.insert(tk.END, "\n".join(formatted))
                else:
                    text_widget.insert(tk.END, result.stdout)
                text_widget.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить данные.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"{e}")
    
    def setup_gpu_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Видеокарта")
        
        info_frame = tk.LabelFrame(frame, text="Информация о видеокарте", bg=self.bg, fg=self.fg, font=('SegoeUI', 11, 'bold'))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_frame = tk.Frame(info_frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gpu_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.gpu_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.gpu_text.yview)
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_gpu_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack()
        
        self.update_gpu_info()
        self.update_gpu_loop()
    
    def update_gpu_loop(self):
        if self.running:
            self.update_gpu_info()
            self.root.after(5000, self.update_gpu_loop)
    
    def update_gpu_info(self):
        info = []
        info.append("=" * 55)
        info.append("ВИДЕОКАРТА (GPU)")
        info.append("=" * 55)
        
        try:
            # Получаем данные через nvidia-smi
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,driver_version,temperature.gpu,utilization.gpu,memory.total,memory.used,memory.free', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                data = [x.strip() for x in result.stdout.strip().split(',')]
                
                info.append(f"\n📌 ОСНОВНЫЕ ДАННЫЕ")
                info.append("-" * 40)
                info.append(f"  Модель: {data[0]}")
                info.append(f"  Драйвер: {data[1]}")
                info.append(f"  Температура: {data[2]}°C")
                info.append(f"  Загрузка: {data[3]}")
                
                info.append(f"\n💾 ПАМЯТЬ")
                info.append("-" * 40)
                info.append(f"  Всего: {data[4]}")
                info.append(f"  Используется: {data[5]}")
                info.append(f"  Свободно: {data[6]}")
                
                # Дополнительная информация через nvidia-smi -q
                result_q = subprocess.run(['nvidia-smi', '-q'], capture_output=True, text=True, timeout=5)
                for line in result_q.stdout.split('\n'):
                    line = line.strip()
                    if 'Product Name' in line:
                        info.append(f"\n📋 ДЕТАЛЬНО")
                        info.append("-" * 40)
                        info.append(f"  {line}")
                    elif 'Bus Location' in line:
                        info.append(f"  {line}")
                    elif 'VBIOS Version' in line:
                        info.append(f"  {line}")
                    elif 'Compute Mode' in line:
                        info.append(f"  {line}")
                    elif 'Max Power Limit' in line:
                        info.append(f"  {line}")
                    elif 'Min Power Limit' in line:
                        info.append(f"  {line}")
                    elif 'Max Clocks' in line:
                        info.append(f"  {line}")
            else:
                info.append("\n❌ nvidia-smi не дал данных")
        except Exception as e:
            info.append(f"\n❌ Ошибка: {e}")
        
        self.gpu_text.delete(1.0, tk.END)
        self.gpu_text.insert(tk.END, "\n".join(info))
    
    def update_battery_loop(self):
        if self.running:
            self.update_battery_info()
            self.root.after(5000, self.update_battery_loop)
    
    def update_battery_info(self):
        if not hasattr(self, 'battery_text'):
            return
        info = []
        info.append("=" * 55)
        info.append("ИНФОРМАЦИЯ О БАТАРЕЕ")
        info.append("=" * 55)
        
        battery_path = None
        if os.path.exists("/sys/class/power_supply/BAT0"):
            battery_path = "/sys/class/power_supply/BAT0"
        elif os.path.exists("/sys/class/power_supply/BAT1"):
            battery_path = "/sys/class/power_supply/BAT1"
        
        if battery_path:
            try:
                with open(f"{battery_path}/uevent", "r") as f:
                    data = {}
                    for line in f:
                        if '=' in line:
                            key, val = line.strip().split('=', 1)
                            data[key] = val
                    
                    info.append(f"Производитель: {data.get('POWER_SUPPLY_MANUFACTURER', 'Неизвестно')}")
                    info.append(f"Технология: {data.get('POWER_SUPPLY_TECHNOLOGY', 'Неизвестно')}")
                    info.append(f"Статус: {data.get('POWER_SUPPLY_STATUS', 'Неизвестно')}")
                    
                    charge_full_design = int(data.get('POWER_SUPPLY_CHARGE_FULL_DESIGN', 0)) / 1000
                    charge_full = int(data.get('POWER_SUPPLY_CHARGE_FULL', 0)) / 1000
                    charge_now = int(data.get('POWER_SUPPLY_CHARGE_NOW', 0)) / 1000
                    capacity = data.get('POWER_SUPPLY_CAPACITY', '0')
                    
                    info.append(f"Проектная ёмкость: {charge_full_design:.0f} мАч")
                    info.append(f"Реальная ёмкость: {charge_full:.0f} мАч")
                    info.append(f"Текущий заряд: {charge_now:.0f} мАч")
                    info.append(f"Заряд: {capacity}%")
                    
                    if charge_full_design > 0:
                        wear = (1 - charge_full / charge_full_design) * 100
                        wear_icon = "⚠️" if wear > 40 else "✅"
                        info.append(f"Износ батареи: {wear_icon} {wear:.0f}%")
                        
                        if hasattr(self, 'save_battery_history'):
                            self.save_battery_history(charge_full_design, charge_full)
                            self.draw_history_graph()
                    
                    voltage_now = int(data.get('POWER_SUPPLY_VOLTAGE_NOW', 0)) / 1000000
                    current_now = int(data.get('POWER_SUPPLY_CURRENT_NOW', 0)) / 1000000
                    info.append(f"Напряжение: {voltage_now:.2f} В")
                    info.append(f"Ток: {current_now:.3f} А")
                    
                    if voltage_now > 0 and current_now > 0:
                        info.append(f"Мощность: {voltage_now * current_now:.1f} Вт")
                    
                    cycle_count = data.get('POWER_SUPPLY_CYCLE_COUNT', '0')
                    if cycle_count != '0':
                        info.append(f"Циклов зарядки: {cycle_count}")
            except Exception as e:
                info.append(f"Ошибка: {e}")
        
        self.battery_text.delete(1.0, tk.END)
        self.battery_text.insert(tk.END, "\n".join(info))
    
    def battery_power_save(self):
        try:
            subprocess.run(['pkexec', 'cpupower', 'frequency-set', '-g', 'powersave'], capture_output=True, timeout=5)
            self.show_notification("Zonlik", "Режим экономии энергии включён")
        except Exception as e:
            self.show_notification("Zonlik", f"Ошибка: {e}")
    
    def battery_calibrate(self):
        result = messagebox.askyesno("Калибровка батареи", 
            "Калибровка батареи:\n\n"
            "1. Батарея будет полностью заряжена\n"
            "2. Затем разряжена до 0%\n"
            "3. Снова заряжена до 100%\n\n"
            "⚠️ Ноутбук должен быть подключён к сети!\n"
            "⚠️ Процесс может занять несколько часов!\n\n"
            "Начать калибровку?")
        
        if not result:
            return
        
        self.show_notification("Zonlik", "Калибровка запущена")
        
        def calibrate_thread():
            try:
                subprocess.run(['pkexec', 'cpupower', 'frequency-set', '-g', 'powersave'], capture_output=True)
                self.root.after(0, lambda: self.show_notification("Zonlik", "Калибровка завершена!"))
            except Exception as e:
                self.root.after(0, lambda: self.show_notification("Zonlik", f"Ошибка: {e}"))
        
        threading.Thread(target=calibrate_thread, daemon=True).start()
    
    def load_battery_history(self):
        history_file = os.path.expanduser("~/.zonlik_battery_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.battery_history = json.load(f)
            except:
                self.battery_history = []
        else:
            self.battery_history = []
    
    def save_battery_history(self, charge_full_design, charge_full):
        import datetime
        wear = (1 - charge_full / charge_full_design) * 100 if charge_full_design > 0 else 0
        
        self.battery_history.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "charge_full": charge_full,
            "charge_full_design": charge_full_design,
            "wear": round(wear, 1)
        })
        
        if len(self.battery_history) > 100:
            self.battery_history = self.battery_history[-100:]
        
        history_file = os.path.expanduser("~/.zonlik_battery_history.json")
        with open(history_file, 'w') as f:
            json.dump(self.battery_history, f)
    
    def draw_history_graph(self):
        if not hasattr(self, 'history_canvas'):
            return
        
        self.history_canvas.delete("all")
        w = self.history_canvas.winfo_width()
        h = self.history_canvas.winfo_height()
        
        if w < 10:
            self.history_canvas.after(100, self.draw_history_graph)
            return
        
        if len(self.battery_history) < 2:
            self.history_canvas.create_text(w//2, h//2, text="Недостаточно данных", fill=self.fg)
            return
        
        history = self.battery_history[-50:]
        max_wear = max([item["wear"] for item in history]) if history else 100
        min_wear = min([item["wear"] for item in history]) if history else 0
        wear_range = max_wear - min_wear if max_wear != min_wear else 1
        
        points = []
        for i, item in enumerate(history):
            x = i * (w / (len(history) - 1))
            y = h - ((item["wear"] - min_wear) / wear_range) * h * 0.9
            points.append((x, y, item["wear"], item["date"]))
        
        for i in range(len(points)-1):
            self.history_canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=self.accent, width=2)
        
        self.history_canvas.create_text(w-5, 5, text=f"Макс износ: {max_wear:.0f}%", fill=self.fg, font=('SegoeUI', 8), anchor='ne')
        self.history_canvas.create_text(w-5, h-5, text=f"Мин износ: {min_wear:.0f}%", fill=self.fg, font=('SegoeUI', 8), anchor='se')
        
        def on_motion(event):
            x = event.x
            if x < 0 or x > w:
                self.history_canvas.delete("tooltip")
                return
            idx = int(x / w * len(points))
            if idx >= len(points):
                idx = len(points) - 1
            wear = points[idx][2]
            date = points[idx][3]
            self.history_canvas.delete("tooltip")
            self.history_canvas.create_text(x, max(10, points[idx][1] - 15), text=f"{date}: {wear:.0f}%", fill=self.accent, font=('SegoeUI', 8), tag="tooltip")
        
        def on_leave(event):
            self.history_canvas.delete("tooltip")
        
        self.history_canvas.bind("<Motion>", on_motion)
        self.history_canvas.bind("<Leave>", on_leave)
    
    def setup_disks_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Диски")
        
        info_frame = tk.LabelFrame(frame, text="Информация о дисках", bg=self.bg, fg=self.fg, font=('SegoeUI', 11, 'bold'))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_frame = tk.Frame(info_frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.disks_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.disks_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.disks_text.yview)
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_disks_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        sudo_btn = tk.Button(btn_frame, text="🔓 Детали дисков (требует пароль)", command=self.request_disk_sudo, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        sudo_btn.pack(side=tk.LEFT, padx=5)
        
        speed_btn = tk.Button(btn_frame, text="💿 Тест скорости", command=self.test_disk_speed, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        speed_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_disks_info()
        self.update_disks_loop()
    
    def update_disks_loop(self):
        if self.running:
            self.update_disks_info()
            self.root.after(10000, self.update_disks_loop)
    
    def request_disk_sudo(self):
        try:
            result = subprocess.run(['pkexec', 'smartctl', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.show_notification("Zonlik", "Права получены. Нажмите 'Обновить'")
                self.update_disks_info()
            else:
                messagebox.showerror("Ошибка", "Не удалось получить права")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def test_disk_speed(self):
        win = tk.Toplevel(self.root)
        win.title("Тест скорости диска")
        win.geometry("500x300")
        win.configure(bg=self.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('Courier', 9), bg=self.graph_bg, fg=self.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "Запуск теста...\n")
        win.update()
        
        try:
            result = subprocess.run(['dd', 'if=/dev/zero', 'of=/tmp/test', 'bs=1M', 'count=100', 'conv=fdatasync'], capture_output=True, text=True)
            text_widget.insert(tk.END, result.stderr)
            subprocess.run(['rm', '/tmp/test'])
        except Exception as e:
            text_widget.insert(tk.END, f"Ошибка: {e}")
        
        text_widget.config(state=tk.DISABLED)
    
    def update_disks_info(self):
        info = []
        info.append("=" * 60)
        info.append("ДИСКИ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,MODEL,SIZE,TYPE,ROTA', '-n'], capture_output=True, text=True)
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    model = ' '.join(parts[1:-3]) if len(parts) > 4 else parts[1]
                    size = parts[-3]
                    rot = parts[-1]
                    
                    is_hdd = rot == '1'
                    if 'nvme' in name.lower():
                        type_icon = "⚡ NVMe SSD"
                    elif is_hdd:
                        type_icon = "💿 HDD"
                    else:
                        type_icon = "⚡ SSD"
                    
                    info.append(f"\n{type_icon} - {model} ({name})")
                    info.append(f"  Объём: {size}")
                    
                    try:
                        result = subprocess.run(['sudo', 'smartctl', '-A', f'/dev/{name}'], capture_output=True, text=True, timeout=3)
                        for line in result.stdout.split('\n'):
                            if 'Temperature_Celsius' in line:
                                parts_temp = line.split()
                                if len(parts_temp) >= 10:
                                    info.append(f"  Температура: {parts_temp[9]}°C")
                                    break
                    except:
                        pass
        except Exception as e:
            info.append(f"Ошибка: {e}")
        
        info.append("\n" + "-" * 40)
        info.append("РАЗДЕЛЫ И ИСПОЛЬЗОВАНИЕ МЕСТА")
        info.append("-" * 40)
        
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                percent = usage.percent
                free_gb = usage.free // (1024**3)
                total_gb = usage.total // (1024**3)
                
                if percent > 90:
                    color = "⚠️ КРИТИЧНО"
                elif percent > 75:
                    color = "⚡ ВНИМАНИЕ"
                else:
                    color = "✅ НОРМА"
                
                info.append(f"{part.mountpoint}: {percent}% занято ({free_gb}/{total_gb} GB) {color}")
            except:
                pass
        
        self.disks_text.delete(1.0, tk.END)
        self.disks_text.insert(tk.END, "\n".join(info))
    
    def setup_usb_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="USB и флешки")
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_usb_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        diagnose_btn = tk.Button(btn_frame, text="🔍 Диагностика", command=self.diagnose_usb, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        diagnose_btn.pack(side=tk.LEFT, padx=5)
        
        fix_btn = tk.Button(btn_frame, text="🛠️ Починка (формат)", command=self.fix_usb, bg='#f38ba8', fg='white', padx=10, pady=4, relief='flat')
        fix_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.usb_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.usb_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.usb_text.yview)
        
        self.update_usb_info()
        self.update_usb_loop()
    
    def update_usb_loop(self):
        if self.running:
            self.update_usb_info()
            self.root.after(10000, self.update_usb_loop)
    
    def update_usb_info(self):
        info = []
        info.append("=" * 60)
        info.append("USB УСТРОЙСТВА И ФЛЕШКИ")
        info.append("=" * 60)
        
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            info.append("\n📌 ПОДКЛЮЧЁННЫЕ USB УСТРОЙСТВА")
            info.append("-" * 40)
            for line in result.stdout.strip().split('\n')[:10]:
                if line:
                    info.append(f"  {line}")
        except:
            pass
        
        info.append("\n💾 USB ФЛЕШКИ")
        info.append("-" * 40)
        
        try:
            result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MODEL', '-l'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'disk' in line and ('usb' in line.lower() or 'sd' in line):
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        size = parts[1]
                        model = ' '.join(parts[2:-1]) if len(parts) > 3 else "Unknown"
                        info.append(f"\n  📀 /dev/{name} | {size} | {model}")
        except Exception as e:
            info.append(f"Ошибка: {e}")
        
        self.usb_text.delete(1.0, tk.END)
        self.usb_text.insert(tk.END, "\n".join(info))
    
    def diagnose_usb(self):
        win = tk.Toplevel(self.root)
        win.title("Диагностика USB")
        win.geometry("600x400")
        win.configure(bg=self.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('Courier', 9), bg=self.graph_bg, fg=self.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            result = subprocess.run(['dmesg', '|', 'grep', '-i', 'usb'], capture_output=True, text=True, shell=True)
            text_widget.insert(tk.END, "ПОСЛЕДНИЕ USB СОБЫТИЯ:\n")
            text_widget.insert(tk.END, "=" * 50 + "\n")
            for line in result.stdout.split('\n')[-30:]:
                text_widget.insert(tk.END, f"{line}\n")
        except Exception as e:
            text_widget.insert(tk.END, f"Ошибка: {e}\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def fix_usb(self):
        win = tk.Toplevel(self.root)
        win.title("Починка USB флешки")
        win.geometry("500x300")
        win.configure(bg=self.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('Courier', 9), bg=self.graph_bg, fg=self.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "ВНИМАНИЕ! ФОРМАТИРОВАНИЕ УДАЛИТ ВСЕ ДАННЫЕ!\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.insert(tk.END, "Для форматирования флешки выполните:\n")
        text_widget.insert(tk.END, "  1. Узнайте устройство: lsblk\n")
        text_widget.insert(tk.END, "  2. Размонтируйте: sudo umount /dev/sdX\n")
        text_widget.insert(tk.END, "  3. Отформатируйте: sudo mkfs.vfat /dev/sdX\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def setup_motherboard_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Материнская плата")
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_motherboard_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        sudo_btn = tk.Button(btn_frame, text="🔓 Полная информация (пароль)", command=self.request_motherboard_sudo, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        sudo_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.motherboard_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.motherboard_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.motherboard_text.yview)
        
        self.update_motherboard_info()
        self.update_motherboard_loop()
    
    def update_motherboard_loop(self):
        if self.running:
            self.update_motherboard_info()
            self.root.after(10000, self.update_motherboard_loop)
    
    def request_motherboard_sudo(self):
        try:
            result = subprocess.run(['pkexec', 'dmidecode', '-t', 'baseboard'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.update_motherboard_info(with_sudo=True)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить права")
        except Exception as e:
            messagebox.showerror("Ошибка", f"{e}")
    
    def update_motherboard_info(self, with_sudo=False):
        info = []
        info.append("=" * 60)
        info.append("МАТЕРИНСКАЯ ПЛАТА")
        info.append("=" * 60)
        
        info.append("\n📌 ОСНОВНАЯ ИНФОРМАЦИЯ")
        info.append("-" * 40)
        
        try:
            with open("/sys/class/dmi/id/board_vendor", "r") as f:
                info.append(f"Производитель: {f.read().strip()}")
        except:
            info.append("Производитель: Неизвестно")
        
        try:
            with open("/sys/class/dmi/id/board_name", "r") as f:
                info.append(f"Модель: {f.read().strip()}")
        except:
            pass
        
        try:
            with open("/sys/class/dmi/id/board_version", "r") as f:
                info.append(f"Версия: {f.read().strip()}")
        except:
            pass
        
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'ISA bridge' in line or 'LPC' in line:
                    info.append(f"Чипсет: {line.strip()}")
                    break
        except:
            pass
        
        if with_sudo:
            info.append("\n" + "=" * 60)
            info.append("ДЕТАЛЬНАЯ ИНФОРМАЦИЯ")
            info.append("=" * 60)
            try:
                result = subprocess.run(['dmidecode', '-t', 'baseboard'], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'Serial Number:' in line:
                        info.append(f"Серийный номер: {line.split(':')[1].strip()}")
                    elif 'Asset Tag:' in line:
                        info.append(f"Asset Tag: {line.split(':')[1].strip()}")
            except:
                info.append("Ошибка получения детальной информации")
        
        info.append("\n💡 Для полной информации нажмите кнопку")
        
        self.motherboard_text.delete(1.0, tk.END)
        self.motherboard_text.insert(tk.END, "\n".join(info))
    
    def setup_system_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Система")
        
        btn_frame = tk.Frame(frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", command=self.update_system_info, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        logs_btn = tk.Button(btn_frame, text="📜 Логи ошибок", command=self.show_error_logs, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        logs_btn.pack(side=tk.LEFT, padx=5)
        
        backup_btn = tk.Button(btn_frame, text="💾 Бэкап настроек", command=self.backup_settings, bg=self.accent, fg='white', padx=10, pady=4, relief='flat')
        backup_btn.pack(side=tk.LEFT, padx=5)
        
        report_btn = tk.Button(btn_frame, text="📊 Отчёт о системе", command=self.system_report, bg=self.secondary, fg='#1a1b26', padx=10, pady=4, relief='flat')
        report_btn.pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.system_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.system_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.system_text.yview)
        
        self.update_system_info()
        self.update_system_loop()
    
    def setup_battery_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Батарея")
        
        text_frame = tk.Frame(frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.battery_text = tk.Text(text_frame, wrap=tk.WORD, font=('SegoeUI', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        self.battery_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.battery_text.yview)
        
        self.update_battery_info()
        self.update_battery_loop()
    
    def update_battery_loop(self):
        if self.running:
            self.update_battery_info()
            self.root.after(5000, self.update_battery_loop)
    
    def update_battery_info(self):
        info = []
        info.append("=" * 55)
        info.append("ИНФОРМАЦИЯ О БАТАРЕЕ")
        info.append("=" * 55)
        
        battery = psutil.sensors_battery()
        if battery:
            info.append(f"\n📊 СОСТОЯНИЕ")
            info.append("-" * 40)
            info.append(f"  Заряд: {battery.percent}%")
            info.append(f"  Время до разряда: {battery.secsleft // 60} мин" if battery.secsleft > 0 else "  На зарядке")
            info.append(f"  Подключена: {'✅' if battery.power_plugged else '❌'}")
        else:
            info.append("\n⚠️ Батарея не обнаружена")
            info.append("  Возможно, это стационарный ПК")
        
        self.battery_text.delete(1.0, tk.END)
        self.battery_text.insert(tk.END, "\n".join(info))

    def update_system_loop(self):
        if self.running:
            self.update_system_info()
            self.root.after(10000, self.update_system_loop)
    
    def show_error_logs(self):
        win = tk.Toplevel(self.root)
        win.title("Логи ошибок")
        win.geometry("800x500")
        win.configure(bg=self.bg)
        
        text_widget = tk.Text(win, wrap=tk.WORD, font=('Courier', 9), bg=self.graph_bg, fg=self.fg)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            result = subprocess.run(['journalctl', '-p', '3', '-n', '50', '--no-pager'], capture_output=True, text=True)
            text_widget.insert(tk.END, result.stdout if result.stdout else "Ошибок не найдено\n")
        except Exception as e:
            text_widget.insert(tk.END, f"Ошибка: {e}\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def backup_settings(self):
        import datetime, shutil
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = os.path.expanduser(f"~/zonlik_backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(self.settings_file):
            shutil.copy(self.settings_file, backup_dir)
        
        history_file = os.path.expanduser("~/.zonlik_battery_history.json")
        if os.path.exists(history_file):
            shutil.copy(history_file, backup_dir)
        
        messagebox.showinfo("Бэкап создан", f"Папка: {backup_dir}")
    
    def system_report(self):
        import datetime
        filename = os.path.expanduser(f"~/system_report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("ОТЧЁТ О СИСТЕМЕ\n")
            f.write(f"Дата: {datetime.datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            
            import platform
            f.write(f"ОС: {platform.system()} {platform.release()}\n")
            f.write(f"Ядро: {platform.version()}\n")
            f.write(f"Хост: {platform.node()}\n\n")
            
            f.write("CPU:\n")
            with open('/proc/cpuinfo', 'r') as cpuinfo:
                for line in cpuinfo:
                    if 'model name' in line:
                        f.write(f"  {line.strip()}\n")
                        break
            f.write(f"  Загрузка: {psutil.cpu_percent()}%\n\n")
            
            f.write("ПАМЯТЬ:\n")
            mem = psutil.virtual_memory()
            f.write(f"  Всего: {mem.total // (1024**3)} GB\n")
            f.write(f"  Используется: {mem.used // (1024**3)} GB\n")
            f.write(f"  Загрузка: {mem.percent}%\n")
        
        messagebox.showinfo("Отчёт создан", filename)
    
    def update_system_info(self):
        info = []
        info.append("=" * 60)
        info.append("СИСТЕМА")
        info.append("=" * 60)
        
        import platform
        info.append(f"ОС: {platform.system()} {platform.release()}")
        info.append(f"Ядро: {platform.version()}")
        info.append(f"Хост: {platform.node()}")
        info.append(f"Архитектура: {platform.machine()}")
        
        info.append("")
        info.append("-" * 40)
        info.append("ЗАГРУЗКА")
        info.append("-" * 40)
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        info.append(f"Время работы: {days}д {hours}ч {minutes}м")
        info.append(f"Загрузка CPU: {psutil.cpu_percent()}%")
        info.append(f"Процессов: {len(psutil.pids())}")
        info.append(f"Пользователей: {len(psutil.users())}")
        
        self.system_text.delete(1.0, tk.END)
        self.system_text.insert(tk.END, "\n".join(info))
    
    def setup_settings_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Настройки")
        
        self.notif_var = tk.BooleanVar(value=self.settings.get("notifications", True))
        notif_check = tk.Checkbutton(frame, text="🔔 Уведомления", variable=self.notif_var, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.toggle_notifications)
        notif_check.pack(anchor='w', pady=8)
        
        theme_frame = tk.Frame(frame, bg=self.bg)
        theme_frame.pack(anchor='w', pady=8)
        tk.Label(theme_frame, text="🎨 Тема: ", bg=self.bg, fg=self.fg).pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.current_theme)
        for theme, name in [("dark_matter", "Dark Matter"), ("cyberpunk", "Cyberpunk"), ("matrix", "Matrix"), ("sunset", "Sunset"), ("ocean", "Ocean"), ("forest", "Forest"), ("royal", "Royal"), ("cherry", "Cherry")]:
            rb = tk.Radiobutton(theme_frame, text=name, variable=self.theme_var, value=theme, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.change_theme)
            rb.pack(side=tk.LEFT, padx=5)
        
        style_frame = tk.Frame(frame, bg=self.bg)
        style_frame.pack(anchor='w', pady=8)
        tk.Label(style_frame, text="📊 Стиль графиков: ", bg=self.bg, fg=self.fg).pack(side=tk.LEFT)
        self.style_var = tk.StringVar(value=self.graph_style)
        simple_rb = tk.Radiobutton(style_frame, text="Экономичный", variable=self.style_var, value="simple", bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.change_graph_style)
        simple_rb.pack(side=tk.LEFT, padx=5)
        fancy_rb = tk.Radiobutton(style_frame, text="Красивый", variable=self.style_var, value="fancy", bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.change_graph_style)
        fancy_rb.pack(side=tk.LEFT, padx=5)
        
        interval_frame = tk.LabelFrame(frame, text="Интервал обновления", bg=self.bg, fg=self.fg, font=('SegoeUI', 10, 'bold'))
        interval_frame.pack(anchor='w', pady=8, fill=tk.X)
        self.interval_var = tk.StringVar(value=str(self.settings.get("update_interval", 1.0)))
        for name, val in [("0.25с", 0.25), ("0.50с", 0.50), ("0.75с", 0.75), ("1.00с", 1.00), ("1.50с", 1.50), ("2.00с", 2.00)]:
            rb = tk.Radiobutton(interval_frame, text=name, variable=self.interval_var, value=str(val), bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.change_update_interval)
            rb.pack(side=tk.LEFT, padx=5)
        
        display_frame = tk.LabelFrame(frame, text="Графики", bg=self.bg, fg=self.fg, font=('SegoeUI', 10, 'bold'))
        display_frame.pack(anchor='w', pady=8, fill=tk.X)
        self.show_cpu_var = tk.BooleanVar(value=self.settings.get("show_cpu_graph", True))
        self.show_ram_var = tk.BooleanVar(value=self.settings.get("show_ram_graph", True))
        self.show_gpu_var = tk.BooleanVar(value=self.settings.get("show_gpu_graph", False))
        self.show_disk_var = tk.BooleanVar(value=self.settings.get("show_disk_graph", True))
        self.show_net_var = tk.BooleanVar(value=self.settings.get("show_net_graph", True))
        
        cb_cpu = tk.Checkbutton(display_frame, text="CPU", variable=self.show_cpu_var, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.save_graph_settings)
        cb_cpu.pack(anchor='w', padx=10)
        cb_ram = tk.Checkbutton(display_frame, text="RAM", variable=self.show_ram_var, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.save_graph_settings)
        cb_ram.pack(anchor='w', padx=10)
        cb_gpu = tk.Checkbutton(display_frame, text="GPU", variable=self.show_gpu_var, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.save_graph_settings)
        cb_gpu.pack(anchor='w', padx=10)
        cb_disk = tk.Checkbutton(display_frame, text="Диск", variable=self.show_disk_var, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.save_graph_settings)
        cb_disk.pack(anchor='w', padx=10)
        cb_net = tk.Checkbutton(display_frame, text="Сеть", variable=self.show_net_var, bg=self.bg, fg=self.fg, selectcolor=self.bg, command=self.save_graph_settings)
        cb_net.pack(anchor='w', padx=10)
    
    def setup_help_tab(self):
        frame = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(frame, text="Помощь")
        
        text_frame = tk.Frame(frame, bg=self.bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10), bg=self.graph_bg, fg=self.fg, yscrollcommand=scrollbar.set)
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=help_text.yview)

        instructions = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ███████╗ ██████╗ ███╗   ██╗██╗     ██╗██╗  ██╗                           ║
║     ╚══███╔╝██╔═══██╗████╗  ██║██║     ██║██║ ██╔╝   Create by: Barinov      ║
║       ███╔╝ ██║   ██║██╔██╗ ██║██║     ██║█████╔╝               Kirill       ║
║      ███╔╝  ██║   ██║██║╚██╗██║██║     ██║██╔═██╗               Sergeevich   ║
║     ███████╗╚██████╔╝██║ ╚████║███████╗██║██║  ██╗                           ║
║     ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚═╝  ╚═╝                           ║
║                                                                              ║
║   ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗                ║
║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝                ║
║   █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝                 ║
║   ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝                  ║
║   ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║                   ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝                   ║
║                                                                              ║
║                    ZONLIK FACTORY PROGRAMM v1.44                             ║
║                "Monitor your system, control your hardware"                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ВКЛАДКА "МОНИТОРИНГ"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Графики CPU, RAM, GPU, дисков, сети в реальном времени
• Наведи мышкой на график — увидишь точное значение
• Кнопка "Показать жирные процессы" — топ-5 процессов по CPU
• Кнопка "Очистить кэш" — удаляет ~/.cache

🔄 ВКЛАДКА "ПРОЦЕССЫ"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Список всех процессов с PID, CPU, RAM
• Выбери процесс и нажми "Убить выбранный"

💻 ВКЛАДКА "ПРОЦЕССОР"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Модель, архитектура, ядра, потоки
• Кэш L2/L3
• Поддерживаемые технологии (SSE, AVX, AVX-512, AES-NI, VT-x)
• Текущая частота, температура, загрузка
• Полный список флагов CPU

🔋 ВКЛАДКА "БАТАРЕЯ"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Производитель, технология, статус
• Проектная и реальная ёмкость, износ в %
• Напряжение, ток, мощность
• Кнопка "Экономия энергии" — переключает CPU в powersave
• Кнопка "Калибровка батареи" — восстановление точности показаний
• График истории износа за последнее время

🖥️ ВКЛАДКИ "ВИДЕОКАРТА", "ДИСКИ", "USB"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Полная информация о GPU, дисках, USB устройствах
• Диагностика и тестирование

⚙️ ВКЛАДКА "НАСТРОЙКИ"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Уведомления о высокой нагрузке
• Выбор темы (8 стилей)
• Стиль графиков (экономичный/красивый)
• Интервал обновления (0.25–2.00 сек)
• Выбор отображаемых графиков

⚠️ СОВЕТЫ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Если GPU показывает "--%" — у тебя драйвер nouveau
• Для полной информации о GPU установи nvidia-driver-390
• Графики дисков и сети заполняются через 30–60 секунд
• Настройки программы хранятся в ~/.zonlik_settings.json

📧 КОНТАКТЫ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Создатель: Кирилл (Zonlik)
"""
        
        help_text.insert(tk.END, instructions)
        help_text.config(state=tk.DISABLED)
    
    def get_gpu_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return None
    
    def get_gpu_temp(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return None
    
    def get_disk_io(self):
        io1 = psutil.disk_io_counters()
        time.sleep(0.5)
        io2 = psutil.disk_io_counters()
        read_speed = (io2.read_bytes - io1.read_bytes) / (1024 * 1024) * 2
        write_speed = (io2.write_bytes - io1.write_bytes) / (1024 * 1024) * 2
        return read_speed, write_speed
    
    def get_network_speed(self):
        net1 = psutil.net_io_counters()
        time.sleep(0.5)
        net2 = psutil.net_io_counters()
        down = (net2.bytes_recv - net1.bytes_recv) / 1024
        up = (net2.bytes_sent - net1.bytes_sent) / 1024
        return down, up
    
    def get_cpu_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return int(f.read().strip()) / 1000
        except:
            return None
    
    def draw_graph(self, canvas, data, color, label):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10:
            canvas.after(100, lambda: self.draw_graph(canvas, data, color, label))
            return
        if len(data) < 2:
            canvas.create_text(w//2, h//2, text=f"{label}: нет данных", fill=self.fg)
            return
        points = []
        max_val = 100
        for i, val in enumerate(data):
            x = i * (w / 60)
            y = h - (val / max_val) * h * 0.85
            points.append((x, y, val))
        if self.graph_style == "fancy":
            for i in range(len(points)-1):
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=color, width=3, capstyle=tk.ROUND)
        else:
            for i in range(len(points)-1):
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=color, width=2)
        canvas.create_text(w-5, h-5, text=label, fill=self.fg, font=('SegoeUI', 8), anchor='se')
        
        def on_motion(event):
            x = event.x
            if x < 0 or x > w:
                canvas.delete("tooltip")
                return
            idx = int(x / w * len(points))
            if idx >= len(points):
                idx = len(points) - 1
            val = points[idx][2]
            canvas.delete("tooltip")
            canvas.create_text(x, max(10, points[idx][1] - 15), text=f"{val:.0f}%", fill=color, font=('SegoeUI', 9, 'bold'), tag="tooltip")
        
        def on_leave(event):
            canvas.delete("tooltip")
        
        canvas.bind("<Motion>", on_motion)
        canvas.bind("<Leave>", on_leave)
    
    def draw_double_graph(self, canvas, data1, data2, color1, color2, label1, label2):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10:
            canvas.after(100, lambda: self.draw_double_graph(canvas, data1, data2, color1, color2, label1, label2))
            return
        if len(data1) < 2:
            canvas.create_text(w//2, h//2, text="нет данных", fill=self.fg)
            return
        max_val = 100
        points1 = []
        points2 = []
        for i, (val1, val2) in enumerate(zip(data1, data2)):
            x = i * (w / 60)
            y1 = h - (val1 / max_val) * h * 0.85
            y2 = h - (val2 / max_val) * h * 0.85
            points1.append((x, y1, val1))
            points2.append((x, y2, val2))
        if self.graph_style == "fancy":
            for i in range(len(points1)-1):
                canvas.create_line(points1[i][0], points1[i][1], points1[i+1][0], points1[i+1][1], fill=color1, width=3, capstyle=tk.ROUND)
                canvas.create_line(points2[i][0], points2[i][1], points2[i+1][0], points2[i+1][1], fill=color2, width=3, capstyle=tk.ROUND)
        else:
            for i in range(len(points1)-1):
                canvas.create_line(points1[i][0], points1[i][1], points1[i+1][0], points1[i+1][1], fill=color1, width=2)
                canvas.create_line(points2[i][0], points2[i][1], points2[i+1][0], points2[i+1][1], fill=color2, width=2)
        canvas.create_text(w-5, h-5, text=f"{label1} / {label2}", fill=self.fg, font=('SegoeUI', 8), anchor='se')
        
        def on_motion(event):
            x = event.x
            if x < 0 or x > w:
                canvas.delete("tooltip")
                return
            idx = int(x / w * len(points1))
            if idx >= len(points1):
                idx = len(points1) - 1
            val1 = points1[idx][2]
            val2 = points2[idx][2]
            canvas.delete("tooltip")
            canvas.create_text(x, max(10, points1[idx][1] - 15), text=f"{label1}: {val1:.0f} | {label2}: {val2:.0f}", fill=color1, font=('SegoeUI', 9, 'bold'), tag="tooltip")
        
        def on_leave(event):
            canvas.delete("tooltip")
        
        canvas.bind("<Motion>", on_motion)
        canvas.bind("<Leave>", on_leave)
    
    def update_stats(self):
        if not self.running:
            return
        
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory().percent
        gpu = self.get_gpu_usage()
        cpu_temp = self.get_cpu_temp()
        gpu_temp = self.get_gpu_temp()
        read_speed, write_speed = self.get_disk_io()
        down, up = self.get_network_speed()
        
        # Обновляем текстовые значения
        self.cpu_val.config(text=f"CPU: {cpu:.0f}%")
        self.ram_val.config(text=f"RAM: {ram:.0f}%")
        self.gpu_val.config(text=f"GPU: {gpu:.0f}%" if gpu else "GPU: --%")
        self.disk_val.config(text=f"DISK: ↓{read_speed:.1f} ↑{write_speed:.1f} MB/s")
        self.net_val.config(text=f"INTERNET: ↓{down:.1f} ↑{up:.1f} KB/s")
        self.cpu_temp_val.config(text=f"🌡️ CPU: {cpu_temp:.1f}°C" if cpu_temp else "🌡️ CPU: --°C")
        self.gpu_temp_val.config(text=f"🌡️ GPU: {gpu_temp}°C" if gpu_temp else "🌡️ GPU: --°C")
        
        # Добавляем данные в историю
        self.cpu_history.append(cpu)
        self.ram_history.append(ram)
        if gpu:
            self.gpu_history.append(gpu)
        self.disk_read_history.append(read_speed)
        self.disk_write_history.append(write_speed)
        self.net_down_history.append(down)
        self.net_up_history.append(up)
        
        # Рисуем графики
        if self.graph_vars.get('cpu', tk.BooleanVar(value=True)).get():
            self.draw_graph(self.canvas_cpu, self.cpu_history, self.accent, "CPU")
        if self.graph_vars.get('ram', tk.BooleanVar(value=True)).get():
            self.draw_graph(self.canvas_ram, self.ram_history, self.accent, "RAM")
        if self.graph_vars.get('gpu', tk.BooleanVar(value=False)).get() and gpu:
            self.draw_graph(self.canvas_gpu, self.gpu_history, self.accent, "GPU")
        elif hasattr(self, 'canvas_gpu'):
            self.canvas_gpu.delete("all")
            self.canvas_gpu.create_text(200, 40, text="GPU нет данных", fill=self.fg)
        if self.graph_vars.get('disk', tk.BooleanVar(value=True)).get():
            self.draw_double_graph(self.canvas_disk, self.disk_read_history, self.disk_write_history, '#89b4fa', '#f38ba8', "чтение", "запись")
        if self.graph_vars.get('net', tk.BooleanVar(value=True)).get():
            self.draw_double_graph(self.canvas_net, self.net_down_history, self.net_up_history, '#89b4fa', '#f38ba8', "↓ загрузка", "↑ отдача")
        
        interval = self.settings.get("update_interval", 1.0)
        self.root.after(int(interval * 1000), self.update_stats)
    
    def update_process_list(self):
        if not self.running:
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pid = proc.info['pid']
                name = proc.info['name'] or "???"
                cpu = proc.info['cpu_percent'] or 0
                mem = proc.info['memory_percent'] or 0
                self.tree.insert('', 'end', values=(pid, name, f"{cpu:.1f}", f"{mem:.1f}"))
            except:
                pass
        self.root.after(5000, self.update_process_list)
    
    def show_fat_processes(self):
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append((proc.info['pid'], proc.info['name'] or "???", proc.info['cpu_percent'] or 0, proc.info['memory_percent'] or 0))
            except:
                pass
        procs.sort(key=lambda x: x[2], reverse=True)
        top5 = procs[:5]
        
        win = tk.Toplevel(self.root)
        win.title("Жирные процессы")
        win.geometry("550x400")
        win.configure(bg=self.bg)
        win.transient(self.root)
        win.grab_set()
        
        tk.Label(win, text="Топ-5 процессов по CPU", font=('SegoeUI', 12, 'bold'), fg=self.accent, bg=self.bg).pack(pady=10)
        
        frame = tk.Frame(win, bg=self.bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        check_vars = []
        for pid, name, cpu, mem in top5:
            if cpu < 5:
                continue
            var = tk.BooleanVar()
            check_vars.append((var, pid, name))
            cb = tk.Checkbutton(frame, text=f"PID {pid} | {name[:50]} | CPU {cpu:.1f}% | RAM {mem:.1f}%", variable=var, bg=self.bg, fg=self.fg, selectcolor=self.bg, anchor='w')
            cb.pack(fill=tk.X, pady=2)
        
        if not check_vars:
            tk.Label(win, text="Нет процессов с высокой нагрузкой", fg=self.fg, bg=self.bg).pack(pady=20)
            return
        
        def kill_selected():
            killed = []
            for var, pid, name in check_vars:
                if var.get():
                    os.system(f"kill -9 {pid}")
                    killed.append(f"{name} (PID {pid})")
            if killed:
                messagebox.showinfo("Zonlik", f"Убиты:\n" + "\n".join(killed))
                win.destroy()
                self.update_process_list()
            else:
                messagebox.showwarning("Zonlik", "Ничего не выбрано")
        
        btn_frame = tk.Frame(win, bg=self.bg)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="✅ Убить", command=kill_selected, bg=self.accent, fg='white', padx=15, pady=5, relief='flat').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Отмена", command=win.destroy, bg=self.secondary, fg='#1a1b26', padx=15, pady=5, relief='flat').pack(side=tk.LEFT, padx=5)
    
    def kill_selected_process(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Zonlik", "Выберите процесс")
            return
        values = self.tree.item(selected[0], 'values')
        if messagebox.askyesno("Zonlik", f"Убить {values[1]} (PID {values[0]})?"):
            os.system(f"kill -9 {values[0]}")
            self.update_process_list()
    
    def quick_clean(self):
        size_before = self.get_folder_size(os.path.expanduser("~/.cache"))
        os.system("rm -rf ~/.cache/* 2>/dev/null")
        size_after = self.get_folder_size(os.path.expanduser("~/.cache"))
        freed = size_before - size_after
        messagebox.showinfo("Zonlik", f"Очищено ~{freed:.1f} MB")
    
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
    
    def check_high_load(self):
        if not self.running:
            return
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        if cpu > 85 and self.notifications_enabled:
            subprocess.run(['notify-send', 'Zonlik', f'⚠️ CPU: {cpu:.0f}%'], capture_output=True)
        if ram > 85 and self.notifications_enabled:
            subprocess.run(['notify-send', 'Zonlik', f'⚠️ RAM: {ram:.0f}%'], capture_output=True)
        self.root.after(60000, self.check_high_load)
    
    def show_notification(self, title, msg):
        if self.notifications_enabled:
            subprocess.run(['notify-send', title, msg, '-t', '2000'], capture_output=True)
    
    def toggle_notifications(self):
        self.notifications_enabled = self.notif_var.get()
        self.settings["notifications"] = self.notifications_enabled
        self.save_settings()
    
    def change_theme(self):
        self.current_theme = self.theme_var.get()
        self.settings["theme"] = self.current_theme
        self.save_settings()
        self.root.destroy()
        os.system(f"python3 {os.path.expanduser('~/Zonlik-Monitor/zonlik_monitor_full.py')} &")
    
    def change_update_interval(self):
        interval = float(self.interval_var.get())
        self.settings["update_interval"] = interval
        self.save_settings()
    
    def change_graph_style(self):
        self.graph_style = self.style_var.get()
        self.settings["graph_style"] = self.graph_style
        self.save_settings()
        self.refresh_graphs()
    
    def save_graph_settings(self):
        self.settings["show_cpu_graph"] = self.show_cpu_var.get()
        self.settings["show_ram_graph"] = self.show_ram_var.get()
        self.settings["show_gpu_graph"] = self.show_gpu_var.get()
        self.settings["show_disk_graph"] = self.show_disk_var.get()
        self.settings["show_net_graph"] = self.show_net_var.get()
        self.save_settings()
        self.root.destroy()
        os.system(f"python3 {os.path.expanduser('~/Zonlik-Monitor/zonlik_monitor_full.py')} &")
    
    def refresh_graphs(self):
        for graph_name, canvas in self.graphs:
            if graph_name == 'cpu':
                self.draw_graph(canvas, self.cpu_history, self.accent, "CPU")
            elif graph_name == 'ram':
                self.draw_graph(canvas, self.ram_history, self.accent, "RAM")
            elif graph_name == 'gpu':
                gpu = self.get_gpu_usage()
                if gpu is not None:
                    self.draw_graph(canvas, self.gpu_history, self.accent, "GPU")
                else:
                    canvas.delete("all")
                    canvas.create_text(canvas.winfo_width()//2, 50, text="GPU данные недоступны", fill=self.fg)
            elif graph_name == 'disk':
                self.draw_double_graph(canvas, self.disk_read_history, self.disk_write_history, '#89b4fa', '#f38ba8', "чтение", "запись")
            elif graph_name == 'net':
                self.draw_double_graph(canvas, self.net_down_history, self.net_up_history, '#89b4fa', '#f38ba8', "↓ загрузка", "↑ отдача")
    
    def on_closing(self):
        self.running = False
        self.root.destroy()
        os._exit(0)

if __name__ == "__main__":
    print(ZONLIK_ASCII)
    print("   Запуск Zonlik Monitor...\n")
    root = tk.Tk()
    app = ZonlikMonitor(root)
    root.mainloop()

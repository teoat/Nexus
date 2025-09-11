#!/usr/bin/env python3
"""
🚀 Nexus Platform Desktop Launcher
Integrated system launcher that starts all services and opens browser
"""

import os
import sys
import json
import time
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import psutil
from datetime import datetime
import queue
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_desktop_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NexusDesktopLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Nexus Platform - Integrated System Launcher")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # System status
        self.systems_status = {
            'python_processes': False,
            'docker_services': False,
            'kubernetes_cluster': False,
            'nexus_app': False,
            'monitoring': False,
            'databases': False
        }
        
        # Process tracking
        self.processes = {}
        self.log_queue = queue.Queue()
        
        # Create UI
        self.create_ui()
        
        # Start log monitoring
        self.start_log_monitoring()
        
    def create_ui(self):
        """Create the main user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🚀 Nexus Platform - Integrated System Launcher",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ Control Panel", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Launch buttons
        self.launch_all_btn = ttk.Button(
            control_frame, 
            text="🚀 Launch All Systems",
            command=self.launch_all_systems,
            style='Accent.TButton'
        )
        self.launch_all_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_all_btn = ttk.Button(
            control_frame,
            text="🛑 Stop All Systems",
            command=self.stop_all_systems,
            state='disabled'
        )
        self.stop_all_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.open_browser_btn = ttk.Button(
            control_frame,
            text="🌐 Open Browser",
            command=self.open_browser,
            state='disabled'
        )
        self.open_browser_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.status_btn = ttk.Button(
            control_frame,
            text="📊 Check Status",
            command=self.check_all_status
        )
        self.status_btn.grid(row=0, column=3)
        
        # System status panel
        status_frame = ttk.LabelFrame(main_frame, text="📊 System Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Status indicators
        self.status_labels = {}
        systems = [
            ('python_processes', '🐍 Python Processes'),
            ('docker_services', '🐳 Docker Services'),
            ('kubernetes_cluster', '☸️ Kubernetes Cluster'),
            ('nexus_app', '🌐 Nexus App Backend'),
            ('monitoring', '📈 Monitoring Stack'),
            ('databases', '🗄️ Database Services')
        ]
        
        for i, (key, label) in enumerate(systems):
            status_frame.columnconfigure(1, weight=1)
            
            ttk.Label(status_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=2
            )
            
            self.status_labels[key] = ttk.Label(
                status_frame, 
                text="❌ Not Running",
                foreground='red'
            )
            self.status_labels[key].grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Log panel
        log_frame = ttk.LabelFrame(main_frame, text="📝 System Logs", padding="10")
        log_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=60,
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Quick access panel
        access_frame = ttk.LabelFrame(main_frame, text="🔗 Quick Access", padding="10")
        access_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        access_buttons = [
            ("🌐 Nexus App", "http://localhost:8000", self.open_nexus_app),
            ("📈 Grafana", "http://localhost:3000", self.open_grafana),
            ("📊 Prometheus", "http://localhost:9090", self.open_prometheus),
            ("🦄 Neo4j", "http://localhost:7474", self.open_neo4j),
            ("📦 MinIO", "http://localhost:9001", self.open_minio),
            ("🐰 RabbitMQ", "http://localhost:15672", self.open_rabbitmq)
        ]
        
        for i, (text, url, command) in enumerate(access_buttons):
            btn = ttk.Button(access_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=400
        )
        self.progress.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # Also log to file
        logger.info(message)
        
    def start_log_monitoring(self):
        """Start monitoring log queue"""
        def check_queue():
            try:
                while True:
                    message = self.log_queue.get_nowait()
                    self.log_message(message)
            except queue.Empty:
                pass
            self.root.after(100, check_queue)
        
        check_queue()
        
    def update_status(self, system, status):
        """Update system status indicator"""
        self.systems_status[system] = status
        
        if status:
            self.status_labels[system].config(text="✅ Running", foreground='green')
        else:
            self.status_labels[system].config(text="❌ Not Running", foreground='red')
            
    def check_python_processes(self):
        """Check if Python processes are running"""
        try:
            # Check for robust parallel worker system
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('robust_parallel_worker_system.py' in cmd for cmd in proc.info['cmdline']):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            self.log_message(f"Error checking Python processes: {e}")
            return False
            
    def check_docker_services(self):
        """Check if Docker services are running"""
        try:
            result = subprocess.run([
                '/Applications/Docker.app/Contents/Resources/bin/docker',
                'compose', '-f', 'docker/docker-compose.simple.yml', 'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                services = json.loads(result.stdout)
                return len(services) > 0
            return False
        except Exception as e:
            self.log_message(f"Error checking Docker services: {e}")
            return False
            
    def check_kubernetes_cluster(self):
        """Check if Kubernetes cluster is running"""
        try:
            result = subprocess.run(['kubectl', 'get', 'pods', '-n', 'nexus-platform'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'Running' in result.stdout
        except Exception as e:
            self.log_message(f"Error checking Kubernetes cluster: {e}")
            return False
            
    def check_nexus_app(self):
        """Check if Nexus app backend is running"""
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            return response.status_code == 200
        except:
            try:
                # Check if uvicorn process is running
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline'] and any('uvicorn' in cmd for cmd in proc.info['cmdline']):
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return False
            except:
                return False
                
    def check_monitoring(self):
        """Check if monitoring services are running"""
        try:
            # Check Prometheus
            response = requests.get('http://localhost:9090', timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def check_databases(self):
        """Check if database services are running"""
        try:
            # Check PostgreSQL
            response = requests.get('http://localhost:5432', timeout=2)
            return True
        except:
            # Check if PostgreSQL container is running
            try:
                result = subprocess.run([
                    '/Applications/Docker.app/Contents/Resources/bin/docker',
                    'ps', '--filter', 'name=nexus-postgresql', '--format', '{{.Status}}'
                ], capture_output=True, text=True, timeout=5)
                return 'Up' in result.stdout
            except:
                return False
                
    def check_all_status(self):
        """Check status of all systems"""
        self.log_message("🔍 Checking system status...")
        
        # Update status indicators
        self.update_status('python_processes', self.check_python_processes())
        self.update_status('docker_services', self.check_docker_services())
        self.update_status('kubernetes_cluster', self.check_kubernetes_cluster())
        self.update_status('nexus_app', self.check_nexus_app())
        self.update_status('monitoring', self.check_monitoring())
        self.update_status('databases', self.check_databases())
        
        # Enable/disable buttons based on status
        all_running = all(self.systems_status.values())
        self.stop_all_btn.config(state='normal' if any(self.systems_status.values()) else 'disabled')
        self.open_browser_btn.config(state='normal' if self.systems_status['nexus_app'] else 'disabled')
        
        self.log_message(f"✅ Status check complete. Systems running: {sum(self.systems_status.values())}/6")
        
    def launch_python_processes(self):
        """Launch Python automation processes"""
        self.log_message("🐍 Starting Python automation processes...")
        
        try:
            # Start robust parallel worker system
            process = subprocess.Popen([
                './nexus_python_env/bin/python', 'robust_parallel_worker_system.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['robust_worker'] = process
            
            # Start SOT comprehensive system
            process = subprocess.Popen([
                './nexus_python_env/bin/python', 'nexus_comprehensive_sot.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['sot_system'] = process
            
            # Start monitoring dashboard
            process = subprocess.Popen([
                './nexus_python_env/bin/python', 'enhanced_monitoring_dashboard.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['monitoring'] = process
            
            self.log_message("✅ Python processes started successfully")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error starting Python processes: {e}")
            return False
            
    def launch_docker_services(self):
        """Launch Docker services"""
        self.log_message("🐳 Starting Docker services...")
        
        try:
            result = subprocess.run([
                'bash', '-c', 
                'export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" && '
                'docker compose -f docker/docker-compose.simple.yml up -d'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_message("✅ Docker services started successfully")
                return True
            else:
                self.log_message(f"❌ Error starting Docker services: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error starting Docker services: {e}")
            return False
            
    def launch_kubernetes_cluster(self):
        """Launch Kubernetes cluster"""
        self.log_message("☸️ Starting Kubernetes cluster...")
        
        try:
            # Start minikube
            result = subprocess.run(['minikube', 'start', '--driver=docker'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Apply Kubernetes configurations
                self.apply_kubernetes_configs()
                self.log_message("✅ Kubernetes cluster started successfully")
                return True
            else:
                self.log_message(f"❌ Error starting Kubernetes cluster: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error starting Kubernetes cluster: {e}")
            return False
            
    def apply_kubernetes_configs(self):
        """Apply Kubernetes configurations"""
        self.log_message("📦 Applying Kubernetes configurations...")
        
        configs = [
            'k8s/optimized/namespace-simple.yaml',
            'k8s/optimized/secrets-simple.yaml',
            'k8s/optimized/postgresql-simple.yaml',
            'k8s/optimized/redis-simple.yaml'
        ]
        
        for config in configs:
            try:
                if os.path.exists(config):
                    result = subprocess.run(['kubectl', 'apply', '-f', config], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        self.log_message(f"✅ Applied {config}")
                    else:
                        self.log_message(f"⚠️ Warning applying {config}: {result.stderr}")
            except Exception as e:
                self.log_message(f"❌ Error applying {config}: {e}")
                
    def launch_nexus_app(self):
        """Launch Nexus app backend"""
        self.log_message("🌐 Starting Nexus app backend...")
        
        try:
            # Start NEXUS app backend
            process = subprocess.Popen([
                './nexus_python_env/bin/uvicorn',
                'NEXUS_app.backend.main_enhanced:app',
                '--host', '0.0.0.0',
                '--port', '8000',
                '--reload'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['nexus_app'] = process
            
            # Wait for app to start
            time.sleep(10)
            
            # Check if app is responding
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get('http://localhost:8000/health', timeout=2)
                    if response.status_code == 200:
                        self.log_message("✅ Nexus app backend started successfully")
                        return True
                except:
                    time.sleep(1)
                    
            self.log_message("⚠️ Nexus app backend may still be starting...")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error starting Nexus app backend: {e}")
            return False
            
    def launch_all_systems(self):
        """Launch all systems in sequence"""
        self.launch_all_btn.config(state='disabled')
        self.progress.start()
        
        def launch_thread():
            try:
                self.log_message("🚀 Starting integrated system launch...")
                
                # Launch systems in order
                systems = [
                    ("Python Processes", self.launch_python_processes),
                    ("Docker Services", self.launch_docker_services),
                    ("Kubernetes Cluster", self.launch_kubernetes_cluster),
                    ("Nexus App Backend", self.launch_nexus_app)
                ]
                
                for name, launcher in systems:
                    self.log_message(f"🔄 Launching {name}...")
                    success = launcher()
                    if not success:
                        self.log_message(f"⚠️ {name} had issues but continuing...")
                    time.sleep(5)  # Wait between launches
                
                # Final status check
                time.sleep(10)
                self.check_all_status()
                
                # Enable browser button if app is running
                if self.systems_status['nexus_app']:
                    self.open_browser()
                
                self.log_message("🎉 System launch completed!")
                
            except Exception as e:
                self.log_message(f"❌ Error during system launch: {e}")
            finally:
                self.progress.stop()
                self.launch_all_btn.config(state='normal')
                
        threading.Thread(target=launch_thread, daemon=True).start()
        
    def stop_all_systems(self):
        """Stop all running systems"""
        self.log_message("🛑 Stopping all systems...")
        
        try:
            # Stop Python processes
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    process.terminate()
                    self.log_message(f"🛑 Stopped {name}")
            
            # Stop Docker services
            try:
                subprocess.run([
                    'bash', '-c', 
                    'export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" && '
                    'docker compose -f docker/docker-compose.simple.yml down'
                ], capture_output=True, text=True, timeout=30)
                self.log_message("🛑 Stopped Docker services")
            except Exception as e:
                self.log_message(f"⚠️ Error stopping Docker services: {e}")
            
            # Stop minikube
            try:
                subprocess.run(['minikube', 'stop'], capture_output=True, text=True, timeout=30)
                self.log_message("🛑 Stopped Kubernetes cluster")
            except Exception as e:
                self.log_message(f"⚠️ Error stopping Kubernetes cluster: {e}")
            
            # Clear process tracking
            self.processes.clear()
            
            # Update status
            self.check_all_status()
            
            self.log_message("✅ All systems stopped")
            
        except Exception as e:
            self.log_message(f"❌ Error stopping systems: {e}")
            
    def open_browser(self):
        """Open browser to Nexus app frontend"""
        self.log_message("🌐 Opening browser to Nexus Platform...")
        
        try:
            # Try to open the main app first
            webbrowser.open('http://localhost:8000')
            
            # Also open monitoring dashboard
            time.sleep(2)
            webbrowser.open('http://localhost:3000')
            
            self.log_message("✅ Browser opened to Nexus Platform")
            
        except Exception as e:
            self.log_message(f"❌ Error opening browser: {e}")
            
    def open_nexus_app(self):
        """Open Nexus app"""
        webbrowser.open('http://localhost:8000')
        
    def open_grafana(self):
        """Open Grafana dashboard"""
        webbrowser.open('http://localhost:3000')
        
    def open_prometheus(self):
        """Open Prometheus"""
        webbrowser.open('http://localhost:9090')
        
    def open_neo4j(self):
        """Open Neo4j browser"""
        webbrowser.open('http://localhost:7474')
        
    def open_minio(self):
        """Open MinIO console"""
        webbrowser.open('http://localhost:9001')
        
    def open_rabbitmq(self):
        """Open RabbitMQ management"""
        webbrowser.open('http://localhost:15672')
        
    def run(self):
        """Run the desktop application"""
        self.log_message("🚀 Nexus Platform Desktop Launcher started")
        self.check_all_status()
        
        # Schedule periodic status checks
        def periodic_check():
            self.check_all_status()
            self.root.after(30000, periodic_check)  # Check every 30 seconds
            
        self.root.after(5000, periodic_check)
        
        # Start the GUI
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = NexusDesktopLauncher()
        app.run()
    except Exception as e:
        print(f"Error starting desktop launcher: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

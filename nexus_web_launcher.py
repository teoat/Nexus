#!/usr/bin/env python3
"""
🚀 Nexus Platform Web Launcher
Web-based system launcher that starts all services and opens browser
"""

import os
import sys
import json
import time
import subprocess
import threading
import webbrowser
import requests
import psutil
from datetime import datetime
import logging
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_web_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NexusWebLauncher:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
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
        self.launch_in_progress = False
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
            
        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.systems_status)
            
        @self.app.route('/api/launch', methods=['POST'])
        def api_launch():
            if self.launch_in_progress:
                return jsonify({'status': 'already_running', 'message': 'Launch already in progress'})
                
            self.launch_in_progress = True
            
            def launch_thread():
                try:
                    self.launch_all_systems()
                finally:
                    self.launch_in_progress = False
                    
            threading.Thread(target=launch_thread, daemon=True).start()
            return jsonify({'status': 'started', 'message': 'Launch started'})
            
        @self.app.route('/api/stop', methods=['POST'])
        def api_stop():
            self.stop_all_systems()
            return jsonify({'status': 'stopped', 'message': 'All systems stopped'})
            
        @self.app.route('/api/check', methods=['POST'])
        def api_check():
            self.check_all_status()
            return jsonify({'status': 'checked', 'systems': self.systems_status})
            
        @self.app.route('/api/open_browser', methods=['POST'])
        def api_open_browser():
            self.open_browser()
            return jsonify({'status': 'opened', 'message': 'Browser opened'})
            
    def check_python_processes(self):
        """Check if Python processes are running"""
        try:
            processes_found = 0
            total_processes = len(['robust_parallel_worker_system.py', 'nexus_comprehensive_sot.py', 'enhanced_monitoring_dashboard.py'])
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('robust_parallel_worker_system.py' in cmd or 'nexus_comprehensive_sot.py' in cmd or 'enhanced_monitoring_dashboard.py' in cmd for cmd in proc.info['cmdline']):
                        processes_found += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return processes_found > 0
        except Exception as e:
            logger.error(f"Error checking Python processes: {e}")
            return False
            
    def check_docker_services(self):
        """Check if Docker services are running"""
        try:
            result = subprocess.run([
                '/Applications/Docker.app/Contents/Resources/bin/docker',
                'compose', '-f', 'docker/docker-compose.simple.yml', 'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                services = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
                return len(services) > 0
            return False
        except Exception as e:
            logger.error(f"Error checking Docker services: {e}")
            return False
            
    def check_kubernetes_cluster(self):
        """Check if Kubernetes cluster is running"""
        try:
            result = subprocess.run(['kubectl', 'get', 'pods', '-n', 'nexus-platform'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'Running' in result.stdout
        except Exception as e:
            logger.error(f"Error checking Kubernetes cluster: {e}")
            return False
            
    def check_nexus_app(self):
        """Check if Nexus app backend is running"""
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            return response.status_code == 200
        except:
            try:
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
            response = requests.get('http://localhost:9090', timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def check_databases(self):
        """Check if database services are running"""
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
        logger.info("🔍 Checking system status...")
        
        self.systems_status['python_processes'] = self.check_python_processes()
        self.systems_status['docker_services'] = self.check_docker_services()
        self.systems_status['kubernetes_cluster'] = self.check_kubernetes_cluster()
        self.systems_status['nexus_app'] = self.check_nexus_app()
        self.systems_status['monitoring'] = self.check_monitoring()
        self.systems_status['databases'] = self.check_databases()
        
        logger.info(f"✅ Status check complete. Systems running: {sum(self.systems_status.values())}/6")
        
    def launch_python_processes(self):
        """Launch Python automation processes"""
        logger.info("🐍 Starting Python automation processes...")
        
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
            
            logger.info("✅ Python processes started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting Python processes: {e}")
            return False
            
    def launch_docker_services(self):
        """Launch Docker services"""
        logger.info("🐳 Starting Docker services...")
        
        try:
            result = subprocess.run([
                'bash', '-c', 
                'export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" && '
                'docker compose -f docker/docker-compose.simple.yml up -d'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Docker services started successfully")
                return True
            else:
                logger.error(f"❌ Error starting Docker services: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Docker services: {e}")
            return False
            
    def launch_kubernetes_cluster(self):
        """Launch Kubernetes cluster"""
        logger.info("☸️ Starting Kubernetes cluster...")
        
        try:
            # Start minikube
            result = subprocess.run(['minikube', 'start', '--driver=docker'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Apply Kubernetes configurations
                self.apply_kubernetes_configs()
                logger.info("✅ Kubernetes cluster started successfully")
                return True
            else:
                logger.error(f"❌ Error starting Kubernetes cluster: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Kubernetes cluster: {e}")
            return False
            
    def apply_kubernetes_configs(self):
        """Apply Kubernetes configurations"""
        logger.info("📦 Applying Kubernetes configurations...")
        
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
                        logger.info(f"✅ Applied {config}")
                    else:
                        logger.warning(f"⚠️ Warning applying {config}: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ Error applying {config}: {e}")
                
    def launch_nexus_app(self):
        """Launch Nexus app backend"""
        logger.info("🌐 Starting Nexus app backend...")
        
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
                        logger.info("✅ Nexus app backend started successfully")
                        return True
                except:
                    time.sleep(1)
                    
            logger.warning("⚠️ Nexus app backend may still be starting...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting Nexus app backend: {e}")
            return False
            
    def launch_all_systems(self):
        """Launch all systems in sequence"""
        logger.info("🚀 Starting integrated system launch...")
        
        # Launch systems in order
        systems = [
            ("Python Processes", self.launch_python_processes),
            ("Docker Services", self.launch_docker_services),
            ("Kubernetes Cluster", self.launch_kubernetes_cluster),
            ("Nexus App Backend", self.launch_nexus_app)
        ]
        
        for name, launcher in systems:
            logger.info(f"🔄 Launching {name}...")
            success = launcher()
            if not success:
                logger.warning(f"⚠️ {name} had issues but continuing...")
            time.sleep(5)  # Wait between launches
        
        # Final status check
        time.sleep(10)
        self.check_all_status()
        
        # Enable browser if app is running
        if self.systems_status['nexus_app']:
            self.open_browser()
        
        logger.info("🎉 System launch completed!")
        
    def stop_all_systems(self):
        """Stop all running systems"""
        logger.info("🛑 Stopping all systems...")
        
        try:
            # Stop Python processes
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    process.terminate()
                    logger.info(f"🛑 Stopped {name}")
            
            # Stop Docker services
            try:
                subprocess.run([
                    'bash', '-c', 
                    'export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" && '
                    'docker compose -f docker/docker-compose.simple.yml down'
                ], capture_output=True, text=True, timeout=30)
                logger.info("🛑 Stopped Docker services")
            except Exception as e:
                logger.warning(f"⚠️ Error stopping Docker services: {e}")
            
            # Stop minikube
            try:
                subprocess.run(['minikube', 'stop'], capture_output=True, text=True, timeout=30)
                logger.info("🛑 Stopped Kubernetes cluster")
            except Exception as e:
                logger.warning(f"⚠️ Error stopping Kubernetes cluster: {e}")
            
            # Clear process tracking
            self.processes.clear()
            
            # Update status
            self.check_all_status()
            
            logger.info("✅ All systems stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping systems: {e}")
            
    def open_browser(self):
        """Open browser to Nexus app frontend"""
        logger.info("🌐 Opening browser to Nexus Platform...")
        
        try:
            # Try to open the main app first
            webbrowser.open('http://localhost:8000')
            
            # Also open monitoring dashboard
            time.sleep(2)
            webbrowser.open('http://localhost:3000')
            
            logger.info("✅ Browser opened to Nexus Platform")
            
        except Exception as e:
            logger.error(f"❌ Error opening browser: {e}")
            
    def run(self):
        """Run the web application"""
        logger.info("🚀 Nexus Platform Web Launcher started")
        self.check_all_status()
        
        # Schedule periodic status checks
        def periodic_check():
            self.check_all_status()
            threading.Timer(30.0, periodic_check).start()
            
        periodic_check()
        
        # Start the web server
        logger.info("🌐 Web launcher available at http://localhost:8080")
        self.app.run(host='0.0.0.0', port=8080, debug=False)

# HTML Template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Nexus Platform - Web Launcher</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .control-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        .btn-danger {
            background: linear-gradient(45deg, #f44336, #da190b);
            color: white;
        }
        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4);
        }
        .btn-info {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            color: white;
        }
        .btn-info:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
        }
        .status-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .status-card h3 {
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-running {
            background: #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        .status-stopped {
            background: #f44336;
            box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
        }
        .quick-access {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .quick-access .btn {
            padding: 12px 20px;
            font-size: 14px;
        }
        .progress {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
            display: none;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            width: 0%;
            transition: width 0.3s ease;
        }
        .logs {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            display: none;
        }
        .log-entry {
            margin: 2px 0;
            padding: 2px 5px;
            border-radius: 3px;
        }
        .log-info { background: rgba(33, 150, 243, 0.2); }
        .log-success { background: rgba(76, 175, 80, 0.2); }
        .log-warning { background: rgba(255, 193, 7, 0.2); }
        .log-error { background: rgba(244, 67, 54, 0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Nexus Platform - Web Launcher</h1>
        
        <div class="control-panel">
            <button class="btn btn-primary" onclick="launchAll()">🚀 Launch All Systems</button>
            <button class="btn btn-danger" onclick="stopAll()">🛑 Stop All Systems</button>
            <button class="btn btn-info" onclick="checkStatus()">📊 Check Status</button>
            <button class="btn btn-info" onclick="openBrowser()">🌐 Open Browser</button>
        </div>
        
        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        
        <div class="status-panel" id="statusPanel">
            <div class="status-card">
                <h3><span class="status-indicator" id="pythonStatus"></span>🐍 Python Processes</h3>
                <p>Robust parallel worker, SOT system, monitoring dashboard</p>
            </div>
            <div class="status-card">
                <h3><span class="status-indicator" id="dockerStatus"></span>🐳 Docker Services</h3>
                <p>PostgreSQL, Redis, Neo4j, MinIO, RabbitMQ, Prometheus, Grafana</p>
            </div>
            <div class="status-card">
                <h3><span class="status-indicator" id="k8sStatus"></span>☸️ Kubernetes Cluster</h3>
                <p>Database services with persistent storage</p>
            </div>
            <div class="status-card">
                <h3><span class="status-indicator" id="appStatus"></span>🌐 Nexus App Backend</h3>
                <p>FastAPI server with health checks</p>
            </div>
            <div class="status-card">
                <h3><span class="status-indicator" id="monitoringStatus"></span>📈 Monitoring Stack</h3>
                <p>Prometheus and Grafana integration</p>
            </div>
            <div class="status-card">
                <h3><span class="status-indicator" id="databaseStatus"></span>🗄️ Database Services</h3>
                <p>Multi-environment database access</p>
            </div>
        </div>
        
        <h2>🔗 Quick Access</h2>
        <div class="quick-access">
            <a href="http://localhost:8000" target="_blank" class="btn btn-info">🌐 Nexus App</a>
            <a href="http://localhost:3000" target="_blank" class="btn btn-info">📈 Grafana</a>
            <a href="http://localhost:9090" target="_blank" class="btn btn-info">📊 Prometheus</a>
            <a href="http://localhost:7474" target="_blank" class="btn btn-info">🦄 Neo4j</a>
            <a href="http://localhost:9001" target="_blank" class="btn btn-info">📦 MinIO</a>
            <a href="http://localhost:15672" target="_blank" class="btn btn-info">🐰 RabbitMQ</a>
        </div>
        
        <div class="logs" id="logs"></div>
    </div>

    <script>
        let launchInProgress = false;
        
        async function launchAll() {
            if (launchInProgress) {
                alert('Launch already in progress!');
                return;
            }
            
            launchInProgress = true;
            document.getElementById('progress').style.display = 'block';
            document.getElementById('logs').style.display = 'block';
            
            try {
                const response = await fetch('/api/launch', { method: 'POST' });
                const result = await response.json();
                
                if (result.status === 'started') {
                    addLog('🚀 Launch started...', 'info');
                    simulateProgress();
                } else {
                    addLog('❌ ' + result.message, 'error');
                }
            } catch (error) {
                addLog('❌ Error: ' + error.message, 'error');
            }
            
            launchInProgress = false;
        }
        
        async function stopAll() {
            try {
                const response = await fetch('/api/stop', { method: 'POST' });
                const result = await response.json();
                addLog('🛑 ' + result.message, 'info');
                updateStatus();
            } catch (error) {
                addLog('❌ Error: ' + error.message, 'error');
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/check', { method: 'POST' });
                const result = await response.json();
                addLog('📊 Status checked', 'success');
                updateStatus();
            } catch (error) {
                addLog('❌ Error: ' + error.message, 'error');
            }
        }
        
        async function openBrowser() {
            try {
                const response = await fetch('/api/open_browser', { method: 'POST' });
                const result = await response.json();
                addLog('🌐 ' + result.message, 'success');
            } catch (error) {
                addLog('❌ Error: ' + error.message, 'error');
            }
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateStatusIndicator('pythonStatus', data.python_processes);
                    updateStatusIndicator('dockerStatus', data.docker_services);
                    updateStatusIndicator('k8sStatus', data.kubernetes_cluster);
                    updateStatusIndicator('appStatus', data.nexus_app);
                    updateStatusIndicator('monitoringStatus', data.monitoring);
                    updateStatusIndicator('databaseStatus', data.databases);
                })
                .catch(error => {
                    addLog('❌ Error checking status: ' + error.message, 'error');
                });
        }
        
        function updateStatusIndicator(elementId, isRunning) {
            const indicator = document.getElementById(elementId);
            if (isRunning) {
                indicator.className = 'status-indicator status-running';
            } else {
                indicator.className = 'status-indicator status-stopped';
            }
        }
        
        function addLog(message, type) {
            const logs = document.getElementById('logs');
            const entry = document.createElement('div');
            entry.className = 'log-entry log-' + type;
            entry.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        function simulateProgress() {
            const progressBar = document.getElementById('progressBar');
            let width = 0;
            const interval = setInterval(() => {
                width += Math.random() * 10;
                if (width >= 100) {
                    width = 100;
                    clearInterval(interval);
                    addLog('🎉 System launch completed!', 'success');
                    updateStatus();
                }
                progressBar.style.width = width + '%';
            }, 500);
        }
        
        // Initial status check
        updateStatus();
        
        // Periodic status updates
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
'''

def main():
    """Main entry point"""
    try:
        app = NexusWebLauncher()
        app.run()
    except Exception as e:
        print(f"Error starting web launcher: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

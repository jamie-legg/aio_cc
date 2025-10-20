#!/usr/bin/env python3
"""Start all services (watcher, API, dashboard) with unified output"""

import subprocess
import sys
import time
import threading
import os
import queue
import signal
from pathlib import Path

# ANSI color codes
COLORS = {
    'RESET': '\033[0m',
    'GREEN': '\033[92m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'YELLOW': '\033[93m',
    'CYAN': '\033[96m',
    'RED': '\033[91m',
}

def colored(text, color):
    """Return colored text"""
    return f"{COLORS.get(color, '')}{text}{COLORS['RESET']}"

def print_header():
    """Print startup header"""
    print()
    print(colored("=" * 50, 'CYAN'))
    print(colored("  Content Creation Platform - Starting", 'CYAN'))
    print(colored("=" * 50, 'CYAN'))
    print()

def print_services_info():
    """Print information about running services"""
    print()
    print(colored("=" * 50, 'CYAN'))
    print(colored("  All Services Started!", 'CYAN'))
    print(colored("=" * 50, 'CYAN'))
    print()
    print(colored("[WATCHER]   ", 'GREEN') + "Monitoring videos folder")
    print(colored("[API]       ", 'BLUE') + "http://localhost:8000")
    print(colored("[SCHEDULER] ", 'YELLOW') + "Auto-posting scheduled videos")
    print(colored("[DASHBOARD] ", 'MAGENTA') + "http://localhost:5173/dashboard")
    print()
    print(colored("Press Ctrl+C to stop all services", 'YELLOW'))
    print()

def enqueue_output(stream, queue):
    """Helper function to read from a stream and put lines in a queue"""
    try:
        for line in iter(stream.readline, ''):
            if line:
                queue.put(line)
    except Exception:
        pass
    finally:
        stream.close()

def stream_output(process, prefix, color):
    """Stream process output with colored prefix"""
    try:
        # Create queues for stdout and stderr
        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()
        
        # Start threads to read from both streams
        stdout_thread = threading.Thread(
            target=enqueue_output,
            args=(process.stdout, stdout_queue),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=enqueue_output,
            args=(process.stderr, stderr_queue),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Read from both queues and print
        while True:
            # Check if process is done and queues are empty
            if process.poll() is not None:
                # Process ended, drain remaining output
                time.sleep(0.1)  # Give threads time to finish
                while not stdout_queue.empty() or not stderr_queue.empty():
                    try:
                        line = stdout_queue.get_nowait()
                        print(colored(f"[{prefix}] ", color) + line.rstrip())
                    except queue.Empty:
                        pass
                    try:
                        line = stderr_queue.get_nowait()
                        print(colored(f"[{prefix}] ", color) + line.rstrip())
                    except queue.Empty:
                        pass
                break
            
            # Read from stdout queue
            try:
                line = stdout_queue.get_nowait()
                print(colored(f"[{prefix}] ", color) + line.rstrip())
            except queue.Empty:
                pass
            
            # Read from stderr queue
            try:
                line = stderr_queue.get_nowait()
                print(colored(f"[{prefix}] ", color) + line.rstrip())
            except queue.Empty:
                pass
            
            # Small delay to prevent CPU spinning
            time.sleep(0.01)
            
    except Exception as e:
        print(colored(f"[{prefix}] Error reading output: {e}", 'RED'))

def kill_process_tree(pid):
    """Kill a process and all its children (Windows-compatible)"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                          capture_output=True, check=False)
        else:  # Unix-like
            import psutil
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except:
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print(colored(f"[WARNING] Error killing process {pid}: {e}", 'YELLOW'))

def main():
    """Main function to start all services"""
    print_header()
    
    # Get project root
    root_dir = Path(__file__).parent.parent
    dashboard_dir = root_dir / "analytics-dashboard"
    
    # Initialize database first
    print(colored("[INIT] Initializing database...", 'CYAN'))
    init_result = subprocess.run(
        ["uv", "run", "python", "scripts/init_database.py"],
        cwd=root_dir,
        capture_output=True,
        text=True
    )
    if init_result.returncode == 0:
        for line in init_result.stdout.strip().split('\n'):
            print(colored(f"[INIT] {line}", 'CYAN'))
    else:
        print(colored(f"[INIT] Warning: {init_result.stderr}", 'YELLOW'))
    print()
    
    processes = []
    threads = []
    shutdown_requested = threading.Event()
    
    def signal_handler(signum, frame):
        """Handle Ctrl+C and other signals"""
        print()
        print(colored("[INFO] Shutdown signal received...", 'YELLOW'))
        shutdown_requested.set()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start clip watcher
        print(colored("[WATCHER] Starting clip watcher...", 'GREEN'))
        watcher_process = subprocess.Popen(
            ["uv", "run", "python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=root_dir
        )
        processes.append(('WATCHER', watcher_process))
        
        # Start output streaming thread
        watcher_thread = threading.Thread(
            target=stream_output,
            args=(watcher_process, "WATCHER", 'GREEN'),
            daemon=True
        )
        watcher_thread.start()
        threads.append(watcher_thread)
        
        # Small delay
        time.sleep(1)
        
        # Start analytics API
        print(colored("[API] Starting analytics API server...", 'BLUE'))
        api_process = subprocess.Popen(
            ["uv", "run", "python", "scripts/analytics/start_analytics.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=root_dir
        )
        processes.append(('API', api_process))
        
        # Start output streaming thread
        api_thread = threading.Thread(
            target=stream_output,
            args=(api_process, "API", 'BLUE'),
            daemon=True
        )
        api_thread.start()
        threads.append(api_thread)
        
        # Wait for API to start
        time.sleep(2)
        
        # Start scheduler daemon
        print(colored("[SCHEDULER] Starting scheduler daemon...", 'YELLOW'))
        scheduler_process = subprocess.Popen(
            ["uv", "run", "python", "src/scheduling/scheduler_daemon.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=root_dir
        )
        processes.append(('SCHEDULER', scheduler_process))
        
        # Start output streaming thread
        scheduler_thread = threading.Thread(
            target=stream_output,
            args=(scheduler_process, "SCHEDULER", 'YELLOW'),
            daemon=True
        )
        scheduler_thread.start()
        threads.append(scheduler_thread)
        
        # Small delay
        time.sleep(1)
        
        # Check if dashboard dependencies are installed
        node_modules = dashboard_dir / "node_modules"
        if not node_modules.exists():
            print(colored("[DASHBOARD] Installing dependencies first...", 'MAGENTA'))
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=dashboard_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if install_result.returncode != 0:
                print(colored(f"[DASHBOARD] Failed to install dependencies: {install_result.stderr}", 'RED'))
                raise Exception("Dashboard npm install failed")
        
        # Start dashboard
        print(colored("[DASHBOARD] Starting analytics dashboard...", 'MAGENTA'))
        dashboard_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=dashboard_dir,
            shell=True
        )
        processes.append(('DASHBOARD', dashboard_process))
        
        # Start output streaming thread
        dashboard_thread = threading.Thread(
            target=stream_output,
            args=(dashboard_process, "DASHBOARD", 'MAGENTA'),
            daemon=True
        )
        dashboard_thread.start()
        threads.append(dashboard_thread)
        
        # Wait a moment for dashboard to start
        time.sleep(3)
        
        # Print services info
        print_services_info()
        
        # Keep running until interrupted
        while not shutdown_requested.is_set():
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(colored(f"[{name}] Process exited with code {process.returncode}", 'RED'))
                    shutdown_requested.set()
                    break
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print()
        print(colored("[INFO] Stopping all services...", 'YELLOW'))
    except Exception as e:
        print(colored(f"[ERROR] {e}", 'RED'))
    finally:
        # Terminate all processes forcefully
        print(colored("[INFO] Stopping all services...", 'YELLOW'))
        for name, process in processes:
            try:
                if process.poll() is None:  # Process still running
                    print(colored(f"[INFO] Stopping {name}...", 'YELLOW'))
                    
                    # First try graceful termination
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                        print(colored(f"[INFO] {name} stopped gracefully", 'GREEN'))
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't stop
                        print(colored(f"[INFO] Force killing {name}...", 'YELLOW'))
                        if os.name == 'nt':
                            # On Windows, kill the entire process tree
                            kill_process_tree(process.pid)
                        else:
                            process.kill()
                        process.wait(timeout=3)
                        print(colored(f"[INFO] {name} force stopped", 'YELLOW'))
            except Exception as e:
                print(colored(f"[ERROR] Error stopping {name}: {e}", 'RED'))
        
        print(colored("\n[INFO] All services stopped", 'GREEN'))
        print(colored("You can now safely close this terminal\n", 'CYAN'))
        sys.exit(0)

if __name__ == "__main__":
    main()



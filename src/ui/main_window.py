"""Main application window."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import threading
from typing import Optional
from managers.config_manager import ConfigManager
from managers.api_client import APIClient
from .auth_window import AuthWindow


class MainWindow:
    """Main application window for Content Creation."""
    
    def __init__(self):
        """Initialize main window."""
        self.root = tk.Tk()
        self.root.title("Content Creation - AI-Powered Social Media Automation")
        self.root.geometry("900x700")
        
        self.config_manager = ConfigManager()
        self.api_client: Optional[APIClient] = None
        self.watcher_running = False
        
        # Check for API key
        config = self.config_manager.get_config()
        if config.api_key and config.use_backend_api:
            self.api_client = APIClient(config.api_key, config.backend_api_url)
            self._create_main_interface()
        else:
            self._show_auth_window()
        
        # Center window
        self._center_window()
    
    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def _show_auth_window(self):
        """Show authentication window."""
        auth = AuthWindow(self.root, self._on_auth_success)
        self.root.wait_window(auth.window)
    
    def _on_auth_success(self, api_key: str):
        """Handle successful authentication."""
        # Save API key
        self.config_manager.set_backend_config(
            api_key=api_key,
            use_backend=True
        )
        
        # Initialize API client
        config = self.config_manager.get_config()
        self.api_client = APIClient(api_key, config.backend_api_url)
        
        # Create main interface
        self._create_main_interface()
    
    def _create_main_interface(self):
        """Create the main application interface."""
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2196F3", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="Content Creation",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Quota badge
        self.quota_label = tk.Label(
            header_frame,
            text="Loading quota...",
            font=("Arial", 11),
            bg="#1976D2",
            fg="white",
            padx=15,
            py=5
        )
        self.quota_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Main content area
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File Watcher Section
        watcher_frame = ttk.LabelFrame(content_frame, text="File Watcher", padding=15)
        watcher_frame.pack(fill=tk.X, pady=10)
        
        self._create_watcher_section(watcher_frame)
        
        # Platform Status Section
        platform_frame = ttk.LabelFrame(content_frame, text="Platform Status", padding=15)
        platform_frame.pack(fill=tk.X, pady=10)
        
        self._create_platform_section(platform_frame)
        
        # Settings Section
        settings_frame = ttk.LabelFrame(content_frame, text="Settings", padding=15)
        settings_frame.pack(fill=tk.X, pady=10)
        
        self._create_settings_section(settings_frame)
        
        # Activity Log
        log_frame = ttk.LabelFrame(content_frame, text="Activity Log", padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self._create_log_section(log_frame)
        
        # Update quota
        self._update_quota()
    
    def _create_watcher_section(self, parent):
        """Create file watcher controls."""
        
        config = self.config_manager.get_config()
        
        # Watch directory
        dir_frame = tk.Frame(parent)
        dir_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(dir_frame, text="Watch Directory:").pack(side=tk.LEFT)
        self.watch_dir_label = tk.Label(
            dir_frame,
            text=config.watch_dir,
            font=("Arial", 10),
            fg="blue"
        )
        self.watch_dir_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            dir_frame,
            text="Change",
            command=self._change_watch_dir
        ).pack(side=tk.LEFT)
        
        # Start/Stop button
        self.watcher_btn = tk.Button(
            parent,
            text="▶ Start Watching",
            command=self._toggle_watcher,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        )
        self.watcher_btn.pack(pady=10)
        
        # Status
        self.watcher_status_label = tk.Label(
            parent,
            text="● Stopped",
            font=("Arial", 10),
            fg="gray"
        )
        self.watcher_status_label.pack()
    
    def _create_platform_section(self, parent):
        """Create platform status indicators."""
        
        platforms = ["Instagram", "YouTube", "TikTok"]
        self.platform_indicators = {}
        
        for platform in platforms:
            frame = tk.Frame(parent)
            frame.pack(side=tk.LEFT, padx=20)
            
            # Status indicator
            canvas = tk.Canvas(frame, width=20, height=20)
            canvas.pack()
            indicator = canvas.create_oval(2, 2, 18, 18, fill="gray", outline="")
            
            tk.Label(frame, text=platform, font=("Arial", 10)).pack()
            
            self.platform_indicators[platform.lower()] = {
                "canvas": canvas,
                "indicator": indicator
            }
        
        # Check platform status
        self._check_platform_status()
    
    def _create_settings_section(self, parent):
        """Create settings controls."""
        
        config = self.config_manager.get_config()
        
        # Platform toggles
        tk.Label(parent, text="Upload to:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        checkbox_frame = tk.Frame(parent)
        checkbox_frame.pack(fill=tk.X, pady=5)
        
        self.instagram_var = tk.BooleanVar(value=config.upload_to_instagram)
        tk.Checkbutton(
            checkbox_frame,
            text="Instagram",
            variable=self.instagram_var,
            command=lambda: self._toggle_platform("instagram", self.instagram_var.get())
        ).pack(side=tk.LEFT, padx=5)
        
        self.youtube_var = tk.BooleanVar(value=config.upload_to_youtube)
        tk.Checkbutton(
            checkbox_frame,
            text="YouTube",
            variable=self.youtube_var,
            command=lambda: self._toggle_platform("youtube", self.youtube_var.get())
        ).pack(side=tk.LEFT, padx=5)
        
        self.tiktok_var = tk.BooleanVar(value=config.upload_to_tiktok)
        tk.Checkbutton(
            checkbox_frame,
            text="TikTok",
            variable=self.tiktok_var,
            command=lambda: self._toggle_platform("tiktok", self.tiktok_var.get())
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_log_section(self, parent):
        """Create activity log."""
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            text_frame,
            height=8,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9)
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Add initial message
        self.log("✅ Application started successfully")
    
    def log(self, message: str):
        """Add message to activity log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def _change_watch_dir(self):
        """Change watch directory."""
        directory = filedialog.askdirectory(title="Select Watch Directory")
        if directory:
            self.config_manager.set_watch_dir(directory)
            self.watch_dir_label.config(text=directory)
            self.log(f"📁 Watch directory changed to: {directory}")
    
    def _toggle_platform(self, platform: str, enabled: bool):
        """Toggle platform upload."""
        self.config_manager.set_upload_platform(platform, enabled)
        status = "enabled" if enabled else "disabled"
        self.log(f"🔄 {platform.capitalize()} upload {status}")
    
    def _toggle_watcher(self):
        """Start/stop file watcher."""
        if not self.watcher_running:
            self._start_watcher()
        else:
            self._stop_watcher()
    
    def _start_watcher(self):
        """Start file watcher."""
        self.watcher_running = True
        self.watcher_btn.config(text="⏸ Stop Watching", bg="#f44336")
        self.watcher_status_label.config(text="● Running", fg="green")
        self.log("▶ File watcher started")
        
        # TODO: Start actual watcher thread
        messagebox.showinfo(
            "File Watcher",
            "File watcher would start here.\nThis will be integrated with the existing clip_watcher module."
        )
    
    def _stop_watcher(self):
        """Stop file watcher."""
        self.watcher_running = False
        self.watcher_btn.config(text="▶ Start Watching", bg="#4CAF50")
        self.watcher_status_label.config(text="● Stopped", fg="gray")
        self.log("⏹ File watcher stopped")
    
    def _update_quota(self):
        """Update quota display."""
        if self.api_client:
            try:
                quota = self.api_client.check_quota()
                if quota:
                    remaining = quota.get("remaining", 0)
                    limit = quota.get("limit", 0)
                    tier = quota.get("tier", "free")
                    
                    if limit == -1:
                        text = f"Quota: Unlimited ({tier.upper()})"
                    else:
                        text = f"Quota: {remaining}/{limit} ({tier.upper()})"
                    
                    self.quota_label.config(text=text)
                else:
                    self.quota_label.config(text="Quota: Error loading")
            except Exception as e:
                self.quota_label.config(text="Quota: Offline")
        else:
            self.quota_label.config(text="Quota: Local Mode")
    
    def _check_platform_status(self):
        """Check platform authentication status."""
        # TODO: Implement platform status checking
        # For now, show as disconnected
        for platform, widgets in self.platform_indicators.items():
            widgets["canvas"].itemconfig(widgets["indicator"], fill="gray")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point for GUI application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()


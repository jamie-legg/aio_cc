"""Authentication window for API key setup."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import requests


class AuthWindow:
    """Login/API key setup window."""
    
    def __init__(self, parent: tk.Tk, on_success: Callable[[str], None]):
        """
        Initialize auth window.
        
        Args:
            parent: Parent window
            on_success: Callback function called with API key on successful auth
        """
        self.parent = parent
        self.on_success = on_success
        self.api_key = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Content Creation - Login")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create window widgets."""
        
        # Title
        title_label = tk.Label(
            self.window,
            text="Content Creation",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            self.window,
            text="AI-Powered Social Media Automation",
            font=("Arial", 12)
        )
        subtitle_label.pack(pady=5)
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Tab 1: API Key
        api_key_frame = ttk.Frame(notebook)
        notebook.add(api_key_frame, text="API Key")
        self._create_api_key_tab(api_key_frame)
        
        # Tab 2: Login (register/login)
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="Login")
        self._create_login_tab(login_frame)
    
    def _create_api_key_tab(self, parent):
        """Create API key input tab."""
        
        # Instructions
        instructions = tk.Label(
            parent,
            text="Enter your API key to get started.\nDon't have one? Create an account in the Login tab.",
            font=("Arial", 10),
            justify=tk.LEFT
        )
        instructions.pack(pady=20)
        
        # API key input
        tk.Label(parent, text="API Key:").pack(pady=5)
        self.api_key_entry = tk.Entry(parent, width=50, show="*")
        self.api_key_entry.pack(pady=5)
        
        # Show/hide button
        self.show_key_var = tk.BooleanVar()
        show_check = tk.Checkbutton(
            parent,
            text="Show API Key",
            variable=self.show_key_var,
            command=self._toggle_api_key_visibility
        )
        show_check.pack(pady=5)
        
        # Connect button
        connect_btn = tk.Button(
            parent,
            text="Connect",
            command=self._connect_with_api_key,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        )
        connect_btn.pack(pady=20)
    
    def _create_login_tab(self, parent):
        """Create login/register tab."""
        
        # Email
        tk.Label(parent, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(parent, width=50)
        self.email_entry.pack(pady=5)
        
        # Password
        tk.Label(parent, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(parent, width=50, show="*")
        self.password_entry.pack(pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=20)
        
        # Login button
        login_btn = tk.Button(
            btn_frame,
            text="Login",
            command=self._login,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15
        )
        login_btn.grid(row=0, column=0, padx=5)
        
        # Register button
        register_btn = tk.Button(
            btn_frame,
            text="Create Account",
            command=self._register,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15
        )
        register_btn.grid(row=0, column=1, padx=5)
    
    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def _connect_with_api_key(self):
        """Connect with API key."""
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return
        
        # Test API key
        if self._test_api_key(api_key):
            self.api_key = api_key
            self.window.destroy()
            self.on_success(api_key)
        else:
            messagebox.showerror("Error", "Invalid API key or connection failed")
    
    def _test_api_key(self, api_key: str) -> bool:
        """Test if API key is valid."""
        try:
            # Try to check quota with the API key
            response = requests.get(
                "http://localhost:8000/api/v1/enrichment/quota",
                headers={"X-API-Key": api_key},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"API key test failed: {e}")
            return False
    
    def _login(self):
        """Login with email and password."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                api_key = data.get("api_key")
                
                messagebox.showinfo(
                    "Success",
                    "Login successful!\n\nYour API key has been saved."
                )
                
                self.api_key = api_key
                self.window.destroy()
                self.on_success(api_key)
            else:
                error = response.json().get("detail", "Login failed")
                messagebox.showerror("Login Failed", error)
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
    
    def _register(self):
        """Register new account."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/auth/register",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 201:
                messagebox.showinfo(
                    "Success",
                    "Account created successfully!\n\nPlease login with your credentials."
                )
                # Clear password field
                self.password_entry.delete(0, tk.END)
            else:
                error = response.json().get("detail", "Registration failed")
                messagebox.showerror("Registration Failed", error)
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
    
    def get_api_key(self) -> Optional[str]:
        """Get the entered API key."""
        return self.api_key


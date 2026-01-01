import os
import json
import requests
import subprocess
import time
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import shutil
import zipfile
from pathlib import Path

# CONFIGURATION
GITHUB_USER = "int-meetmovaliya-jpg"
REPO_NAME = "Csv_Sql_Engine_Pro"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/version.json"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/latest"
ZIP_URL_TEMPLATE = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/archive/refs/heads/main.zip"

# Get the directory where the application is installed
if getattr(sys, 'frozen', False):
    # If running as a compiled executable
    APP_DIR = Path(sys.executable).parent.parent if sys.platform == 'darwin' else Path(sys.executable).parent
else:
    # If running as a script
    APP_DIR = Path(__file__).parent

CONFIG_DIR = APP_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "update_preferences.json"
VERSION_FILE = APP_DIR / "version.json"

def ensure_config_dir():
    """Ensure config directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_update_preferences():
    """Load user's update preferences"""
    ensure_config_dir()
    default_prefs = {
        "skip_version": None,
        "skip_until_date": None,
        "auto_check": True
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                prefs = json.load(f)
                return {**default_prefs, **prefs}
        except:
            pass
    return default_prefs

def save_update_preferences(prefs):
    """Save user's update preferences"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)

def get_local_version():
    """Get the local version of the application"""
    try:
        if VERSION_FILE.exists():
            with open(VERSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
    except Exception as e:
        print(f"Error reading version: {e}")
    return "0.0.0"

def compare_versions(local, remote):
    """Compare version strings (e.g., "1.0.0" vs "1.0.1")"""
    local_parts = [int(x) for x in local.split('.')]
    remote_parts = [int(x) for x in remote.split('.')]
    
    # Pad with zeros if needed
    max_len = max(len(local_parts), len(remote_parts))
    local_parts += [0] * (max_len - len(local_parts))
    remote_parts += [0] * (max_len - len(remote_parts))
    
    for l, r in zip(local_parts, remote_parts):
        if r > l:
            return True
        elif l > r:
            return False
    return False

def check_for_updates():
    """Check for available updates from GitHub"""
    prefs = load_update_preferences()
    
    # Check if user skipped this version
    remote_version = None
    try:
        response = requests.get(VERSION_URL, timeout=10)
        if response.status_code == 200:
            remote_data = response.json()
            remote_version = remote_data.get("version", "0.0.0")
            
            # If user skipped this version, don't show update
            if prefs.get("skip_version") == remote_version:
                return None
    except Exception as e:
        print(f"Update check failed: {e}")
        return None
    
    if not remote_version:
        return None
    
    local_version = get_local_version()
    
    if compare_versions(local_version, remote_version):
        try:
            response = requests.get(VERSION_URL, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching update info: {e}")
    
    return None

def perform_update(remote_data):
    """Perform the update with user confirmation"""
    root = tk.Tk()
    root.withdraw()
    
    version = remote_data.get('version', 'Unknown')
    changelog = remote_data.get('changelog', ['Bug fixes and improvements'])
    
    # Create a custom dialog
    dialog = tk.Toplevel(root)
    dialog.title("Update Available")
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Title
    title_label = tk.Label(
        dialog, 
        text=f"New Version Available: {version}",
        font=("Arial", 14, "bold"),
        pady=10
    )
    title_label.pack()
    
    # Current version info
    current_label = tk.Label(
        dialog,
        text=f"Current version: {get_local_version()}",
        font=("Arial", 10),
        fg="gray"
    )
    current_label.pack()
    
    # Changelog
    changelog_frame = tk.Frame(dialog)
    changelog_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    
    changelog_label = tk.Label(
        changelog_frame,
        text="What's New:",
        font=("Arial", 10, "bold")
    )
    changelog_label.pack(anchor=tk.W)
    
    changelog_text = tk.Text(
        changelog_frame,
        height=10,
        wrap=tk.WORD,
        font=("Arial", 9)
    )
    changelog_text.pack(fill=tk.BOTH, expand=True)
    changelog_text.insert(tk.END, "\n".join([f"• {item}" for item in changelog]))
    changelog_text.config(state=tk.DISABLED)
    
    scrollbar = tk.Scrollbar(changelog_frame, orient=tk.VERTICAL, command=changelog_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    changelog_text.config(yscrollcommand=scrollbar.set)
    
    # Buttons frame
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    result = {"action": None}
    
    def on_update():
        result["action"] = "update"
        dialog.destroy()
    
    def on_skip():
        result["action"] = "skip"
        dialog.destroy()
    
    def on_later():
        result["action"] = "later"
        dialog.destroy()
    
    update_btn = tk.Button(
        button_frame,
        text="Update Now",
        command=on_update,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        width=12,
        padx=10
    )
    update_btn.pack(side=tk.LEFT, padx=5)
    
    skip_btn = tk.Button(
        button_frame,
        text="Skip This Version",
        command=on_skip,
        bg="#FF9800",
        fg="white",
        font=("Arial", 10),
        width=12,
        padx=10
    )
    skip_btn.pack(side=tk.LEFT, padx=5)
    
    later_btn = tk.Button(
        button_frame,
        text="Remind Me Later",
        command=on_later,
        bg="#9E9E9E",
        fg="white",
        font=("Arial", 10),
        width=12,
        padx=10
    )
    later_btn.pack(side=tk.LEFT, padx=5)
    
    dialog.wait_window()
    root.destroy()
    
    action = result["action"]
    
    if action == "skip":
        # Save preference to skip this version
        prefs = load_update_preferences()
        prefs["skip_version"] = version
        save_update_preferences(prefs)
        return False
    
    if action == "later":
        # User chose to be reminded later (no action needed)
        return False
    
    if action == "update":
        # Perform the update
        try:
            print("Downloading update...")
            
            # Download the latest code from GitHub
            zip_path = APP_DIR / "update.zip"
            response = requests.get(ZIP_URL_TEMPLATE, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the update
            temp_dir = APP_DIR / "temp_update"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the extracted directory
            extracted_dir = temp_dir / f"{REPO_NAME}-main"
            
            if not extracted_dir.exists():
                # Try alternative naming
                subdirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                if subdirs:
                    extracted_dir = subdirs[0]
            
            if extracted_dir.exists():
                # Copy files (excluding certain directories)
                exclude_dirs = {'venv', '__pycache__', '.git', 'build', 'dist', '.DS_Store'}
                exclude_files = {'.gitignore', 'README.md'}
                
                for item in extracted_dir.iterdir():
                    if item.name in exclude_dirs or item.name in exclude_files:
                        continue
                    
                    dest = APP_DIR / item.name
                    
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                
                # Update version file
                version_source = extracted_dir / "version.json"
                if version_source.exists():
                    shutil.copy2(version_source, VERSION_FILE)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            if zip_path.exists():
                zip_path.unlink()
            
            messagebox.showinfo(
                "Update Successful",
                f"Update to version {version} installed successfully!\n\nThe application will restart."
            )
            return True
            
        except Exception as e:
            messagebox.showerror(
                "Update Error",
                f"Failed to update: {str(e)}\n\nPlease try again later or update manually from GitHub."
            )
            import traceback
            traceback.print_exc()
    
    return False

def launch_app():
    """Launch the main application"""
    print("Launching CSV SQL Engine Pro...")
    
    # Determine the script path
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if sys.platform == 'darwin':
            # macOS app bundle
            script_path = APP_DIR / "Resources" / "ui_streamlit.py"
            python_exe = sys.executable
        else:
            script_path = APP_DIR / "ui_streamlit.py"
            python_exe = sys.executable
    else:
        # Running as script
        script_path = APP_DIR / "ui_streamlit.py"
        python_exe = sys.executable
    
    # Fallback if script not found in Resources
    if not script_path.exists():
        script_path = APP_DIR / "ui_streamlit.py"
    
    if not script_path.exists():
        print(f"Error: Could not find ui_streamlit.py at {script_path}")
        messagebox.showerror(
            "Error",
            f"Could not find ui_streamlit.py\n\nExpected at: {script_path}"
        )
        return
    
    # Change to app directory
    os.chdir(APP_DIR)
    
    # Run streamlit
    try:
        process = subprocess.Popen([
            python_exe, "-m", "streamlit", "run",
            str(script_path),
            "--server.port", "8503",
            "--server.headless", "true",
            "--server.address", "127.0.0.1"
        ])
        
        # Open browser after a short delay
        time.sleep(3)
        import webbrowser
        webbrowser.open("http://127.0.0.1:8503")
        
        # Keep the bootstrap alive while streamlit is running
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
    except Exception as e:
        print(f"Error launching app: {e}")
        messagebox.showerror("Error", f"Failed to launch application: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check for updates
    prefs = load_update_preferences()
    if prefs.get("auto_check", True):
        remote_update = check_for_updates()
        if remote_update:
            if perform_update(remote_update):
                # Restart the application after update
                try:
                    if getattr(sys, 'frozen', False):
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                    else:
                        os.execv(sys.executable, [sys.executable] + sys.argv[0])
                except:
                    # Fallback: just launch the app
                    pass
    
    launch_app()

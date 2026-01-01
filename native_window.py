"""
Native macOS window wrapper for Streamlit application
Uses PyQt5 to create a native window with embedded web view
"""
import sys
import time
import subprocess
import threading
from pathlib import Path

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl, QTimer, pyqtSignal, QObject
    from PyQt5.QtGui import QIcon
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

def wait_for_server(url="http://127.0.0.1:8503", timeout=30):
    """Wait for the Streamlit server to be ready"""
    import requests
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

class NativeStreamlitWindow(QMainWindow):
    """Native macOS window containing the Streamlit app"""
    
    def __init__(self, url="http://127.0.0.1:8503", app_name="CSV SQL Engine Pro"):
        super().__init__()
        self.url = url
        self.app_name = app_name
        self.streamlit_process = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(self.app_name)
        
        # Set window size (macOS native sizing)
        screen = QApplication.primaryScreen().geometry()
        window_width = min(1600, int(screen.width() * 0.9))
        window_height = min(1000, int(screen.height() * 0.9))
        self.setGeometry(100, 100, window_width, window_height)
        
        # Center window on screen
        self.center_window()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)
        
        # Set window properties for macOS
        self.setWindowIcon(QIcon())
        
        # macOS specific styling (PyQt5 handles native look automatically)
        
    def center_window(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen().geometry().center()
        frame_geometry.moveCenter(screen)
        self.move(frame_geometry.topLeft())
        
    def load_streamlit_app(self):
        """Load the Streamlit application in the web view"""
        # Wait for server to be ready
        if wait_for_server(self.url):
            self.webview.setUrl(QUrl(self.url))
        else:
            print(f"Error: Streamlit server at {self.url} did not start in time")
            self.show_error_message()
    
    def show_error_message(self):
        """Show error message if server fails to start"""
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Failed to start application server")
        msg.setInformativeText("Please check the console for error messages.")
        msg.exec_()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Terminate Streamlit process if it exists
        if self.streamlit_process:
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=5)
            except:
                self.streamlit_process.kill()
        event.accept()

def launch_native_app(script_path, port=8503, app_name="CSV SQL Engine Pro"):
    """
    Launch Streamlit in a native macOS window
    
    Args:
        script_path: Path to the Streamlit script
        port: Port number for Streamlit server
        app_name: Name of the application
    """
    if not PYQT5_AVAILABLE:
        print("PyQt5 not available. Falling back to browser mode.")
        print("Install PyQt5 with: pip install PyQt5 PyQtWebEngine")
        return launch_browser_fallback(script_path, port)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(app_name)
    
    # Start Streamlit server in background
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        str(script_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false"
    ])
    
    # Create and show native window
    window = NativeStreamlitWindow(
        url=f"http://127.0.0.1:{port}",
        app_name=app_name
    )
    window.streamlit_process = streamlit_process
    window.show()
    
    # Load the app after a short delay
    QTimer.singleShot(1000, window.load_streamlit_app)
    
    # Run the application
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        streamlit_process.terminate()
        sys.exit(0)

def launch_browser_fallback(script_path, port=8503):
    """Fallback to browser mode if PyQt5 is not available"""
    import subprocess
    import time
    import webbrowser
    
    process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        str(script_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "127.0.0.1"
    ])
    
    time.sleep(3)
    webbrowser.open(f"http://127.0.0.1:{port}")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    # Test the native window
    if len(sys.argv) > 1:
        script_path = Path(sys.argv[1])
    else:
        script_path = Path(__file__).parent / "ui_streamlit.py"
    
    launch_native_app(script_path)


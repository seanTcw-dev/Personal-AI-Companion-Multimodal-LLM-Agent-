import sys
import os
import random
import time
import asyncio
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer, QUrl, QPoint, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QMouseEvent, QCursor, QRegion, QIcon
from websocket_server import PositionWebSocketServer

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window Setup - Full Screen, Transparent, Click-through
        self.setWindowTitle("Anime Desktop Pet")
        
        # Set window & taskbar icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'desktop-pet-icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # No window border
            Qt.WindowType.WindowStaysOnTopHint        # Always on top
            # Qt.WindowType.Tool                      # REMOVED to show in taskbar
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Transparent background
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # REMOVED to allow clicking!
        
        # Get Screen Dimensions
        screen = QApplication.primaryScreen()
        if screen is None:
            raise RuntimeError("No primary screen detected")
        self.screen_geometry = screen.availableGeometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        
        # Set window to cover the entire screen
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        
        # Web Engine View
        self.webview = QWebEngineView(self)
        self.webview.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        page = self.webview.page()
        if page is not None:
            page.setBackgroundColor(Qt.GlobalColor.transparent)
        self.setCentralWidget(self.webview)
        
        # Dynamic mask - will be updated by WebSocket
        # Start with a small default mask at bottom center
        self.current_mask = QRegion(self.screen_width // 2 - 100, self.screen_height - 400, 200, 400)
        self.setMask(self.current_mask)
        
        # Dialog mask region (None when dialog is hidden)
        self.dialog_region = None
        
        # Position smoothing
        self.last_x = self.screen_width // 2
        self.last_y = self.screen_height - 200
        self.smoothing_factor = 0.3  # Lower = smoother but slower response
        
        # Load the frontend view
        # We need to point to the specific route we created
        self.webview.setUrl(QUrl("http://localhost:5173/desktop-pet"))
        
        # Start WebSocket server in separate thread
        self.ws_server = PositionWebSocketServer()
        self.ws_server.set_callback(self.update_mask)
        self.ws_server.set_dialog_callback(self.update_dialog_mask)
        self.ws_thread = threading.Thread(target=self.run_websocket_server, daemon=True)
        self.ws_thread.start()
    
    def run_websocket_server(self):
        """Run WebSocket server in separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.ws_server.run_forever())
    
    def update_mask(self, x: int, y: int, width: int, height: int):
        """Update window mask based on character position with smoothing"""
        # Apply smoothing to prevent jittery updates
        smooth_x = int(self.last_x + (x - self.last_x) * self.smoothing_factor)
        smooth_y = int(self.last_y + (y - self.last_y) * self.smoothing_factor)
        
        self.last_x = smooth_x
        self.last_y = smooth_y
        
        # Create mask region centered on character
        # Add some padding to ensure full character is captured
        padding = 20
        mask_x = max(0, smooth_x - width // 2 - padding)
        mask_y = max(0, smooth_y - height // 2 - padding)
        mask_width = min(width + padding * 2, self.screen_width - mask_x)
        mask_height = min(height + padding * 2, self.screen_height - mask_y)
        
        # Character region
        char_region = QRegion(mask_x, mask_y, mask_width, mask_height)
        
        # Merge with dialog region if visible
        if self.dialog_region is not None:
            combined = char_region.united(self.dialog_region)
            self.setMask(combined)
        else:
            self.setMask(char_region)
    
    def update_dialog_mask(self, visible: bool, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        """Update the dialog mask region"""
        if visible:
            padding = 20
            dlg_x = max(0, x - width // 2 - padding)
            dlg_y = max(0, y - height // 2 - padding)
            dlg_w = min(width + padding * 2, self.screen_width - dlg_x)
            dlg_h = min(height + padding * 2, self.screen_height - dlg_y)
            self.dialog_region = QRegion(dlg_x, dlg_y, dlg_w, dlg_h)
        else:
            self.dialog_region = None
        
        # Re-apply current mask with/without dialog
        self.update_mask(self.last_x, self.last_y, 200, 450)

    def contextMenuEvent(self, event):
        if event is None:
            return
        context_menu = QMenu(self)
        exit_action = context_menu.addAction("Exit Desktop Pet")
        action = context_menu.exec(event.globalPos())
        if action == exit_action:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app-level icon (shows in taskbar)
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'desktop-pet-icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Flags for transparency
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--transparent-visuals --disable-gpu-compositing"
    
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())

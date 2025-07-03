import sys
import os
import subprocess
from pathlib import Path

# Use PySide6 for consistency with main GUI
try:
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PySide6.QtGui import QIcon, QAction
    from PySide6.QtCore import Qt
    print("✅ Using PySide6 for tray app")
except ImportError:
    print("❌ PySide6 not available, falling back to PyQt6")
    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PyQt6.QtGui import QIcon, QAction
    from PyQt6.QtCore import Qt

class UnicornTrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        self.tray_icon = QSystemTrayIcon(self)
        
        # Use unicorn-aware.png icon
        icon_path = Path(__file__).parent / "unicorn-aware.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
            print(f"✅ Using custom icon: {icon_path}")
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("applications-other"))
            print("⚠️ Custom icon not found, using theme icon")
            
        self.tray_icon.setToolTip("🦄 Unicorn Commander - NPU Voice Assistant Pro")

        # Connect the activated signal to handle clicks
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.menu = QMenu()

        self.launch_gui_action = QAction("Launch Main GUI", self)
        self.launch_gui_action.triggered.connect(self.launch_main_gui)
        self.menu.addAction(self.launch_gui_action)

        self.menu.addSeparator()

        self.wake_word_action = QAction("Toggle Wake Word", self)
        self.wake_word_action.setCheckable(True)
        self.wake_word_action.setChecked(True)
        self.wake_word_action.triggered.connect(self.toggle_wake_word)
        self.menu.addAction(self.wake_word_action)

        self.voice_activation_action = QAction("Toggle Voice Activation", self)
        self.voice_activation_action.setCheckable(True)
        self.voice_activation_action.setChecked(True)
        self.voice_activation_action.triggered.connect(self.toggle_voice_activation)
        self.menu.addAction(self.voice_activation_action)

        self.menu.addSeparator()

        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.exit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        """Handle activation of the tray icon (clicks)."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger: # This is typically a left-click
            self.launch_main_gui()
        # Other reasons (like Context or MiddleClick) are handled by default or can be added here

    def launch_main_gui(self):
        print("Launching main Unicorn Commander GUI...")
        script_path = os.path.join(os.path.dirname(__file__), "whisperx_npu_gui_qt6.py")
        subprocess.Popen(["python3", script_path])

    def toggle_wake_word(self):
        is_checked = self.wake_word_action.isChecked()
        print(f"Wake Word Toggled: {'ON' if is_checked else 'OFF'}")

    def toggle_voice_activation(self):
        is_checked = self.voice_activation_action.isChecked()
        print(f"Voice Activation Toggled: {'ON' if is_checked else 'OFF'}")

    def quit_app(self):
        print("Exiting Unicorn Commander Tray App.")
        self.tray_icon.hide()
        self.quit()

if __name__ == "__main__":
    app = UnicornTrayApp(sys.argv)
    sys.exit(app.exec())

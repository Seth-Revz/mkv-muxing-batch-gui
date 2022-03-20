import PySide2
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QMainWindow, QFrame, QVBoxLayout

from packages.Startup import GlobalFiles
from packages.Startup.DefaultOptions import DefaultOptions
from packages.Startup.InitializeScreenResolution import width_factor, height_factor
from packages.Startup.Version import Version
from packages.Tabs.GlobalSetting import GlobalSetting
from packages.Tabs.TabsManager import TabsManager
from packages.Widgets.CloseDialog import CloseDialog


def check_if_exit_when_muxing_on():
    if GlobalSetting.MUXING_ON:
        close_dialog = CloseDialog()
        close_dialog.execute()
        if close_dialog.result == "Exit":
            return True
        else:
            return False
    else:
        return True


class MainWindowNonWindowsSystem(QMainWindow):
    def __init__(self, args, parent=None):
        super().__init__(parent=parent)
        self.resize(int(width_factor * 1100), int(height_factor * 635))
        self.setWindowTitle("MKV Muxing Batch GUI v" + str(Version))
        self.setWindowIcon(GlobalFiles.AppIcon)
        self.tabs = TabsManager()
        self.tabs_frame = QFrame()
        self.tabs_layout = QVBoxLayout()
        self.setup_tabs_layout()
        self.setCentralWidget(self.tabs_frame)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show_window()
        self.tabs.set_default_directories()
        self.connect_signals()

    def connect_signals(self):
        self.tabs.currentChanged.connect(self.update_minimum_size)

    def show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def setup_tabs_layout(self):
        self.tabs_frame.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setContentsMargins(9, 9, 9, 12)
        self.tabs_layout.addWidget(self.tabs)
        self.tabs_frame.setLayout(self.tabs_layout)

    def update_minimum_size(self):
        self.setMinimumSize(self.minimumSizeHint())

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        want_to_exit = check_if_exit_when_muxing_on()
        if want_to_exit:
            super().closeEvent(event)
        else:
            event.ignore()

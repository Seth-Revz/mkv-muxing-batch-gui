# -*- coding: utf-8 -*-
import signal
import sys
from traceback import format_exception
from datetime import datetime
import psutil
from PySide2.QtGui import QFont, QFontDatabase, QPalette, QColor
from PySide2.QtWidgets import QApplication
from packages.Startup import GlobalFiles
from packages.Startup.MainApplication import MainApplication
from packages.Widgets.WarningDialog import WarningDialog
import faulthandler

if sys.platform == "win32":
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    from packages.MainWindow import MainWindow
else:
    from packages.MainWindowNonWindowsSystem import MainWindowNonWindowsSystem as MainWindow

# faulthandler.enable()
window: MainWindow
app: QApplication


def setup_application_font():
    try:
        id = QFontDatabase.addApplicationFont(GlobalFiles.MyFontPath)
        _fontstr = QFontDatabase.applicationFontFamilies(id)[0]
        _font = QFont(_fontstr, 10)
        app.setFont(_font)
    except Exception as e:
        warning_dialog = WarningDialog(window_title="Missing Fonts", info_message="Can't find 'OpenSans' font at "
                                                                                  "../Resources/Fonts/OpenSans.ttf\n" +
                                                                                  "application will use default font")
        warning_dialog.execute()


def setup_application_style():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

def create_application():
    global app
    app = MainApplication
    app.setWindowIcon(GlobalFiles.AppIcon)


def create_window():
    global window
    window = MainWindow(sys.argv)


def run_application():
    app_execute = app.exec_()
    kill_all_children()
    sys.exit(app_execute)


def kill_all_children():
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    for child in children:
        child.send_signal(signal.SIGTERM)


def logger_exception(exception_type, exception_value, exception_trace_back):
    with open(GlobalFiles.AppLogFilePath, 'a+', encoding="UTF-8") as log_file:
        log_file.write(str(datetime.utcnow()) + '\n')
        for string in format_exception(exception_type, exception_value, exception_trace_back):
            log_file.write(string)


def setup_logger():
    sys.excepthook = logger_exception


if __name__ == "__main__":
    setup_logger()
    create_application()
    setup_application_font()
    setup_application_style()
    create_window()
    run_application()

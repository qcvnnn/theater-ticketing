"""Start from any working directory: python path/to/main.py."""
import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
import db

def main():
    os.chdir(Path(__file__).resolve().parent)
    app = QApplication(sys.argv)
    def report_error(kind, value, traceback):
        QMessageBox.critical(None, 'Ошибка', db.friendly_error(value))
    sys.excepthook = report_error
    from windows.windows import BaseWindow
    window = BaseWindow()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())

import sys

from config import Config
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QFileDialog

from GUI.controller import FiPaController
from GUI.main_window import FiPaMainWindow
import Model.class_analysis as ca #muss nach matplotlib importiert werden, sonst gibt es Fehler!


def main():
    fipa_app = QApplication([])
    fipa_window = FiPaMainWindow()
    fipa_window.show()
    fipa = FiPaController(model=ca.TransactionAnalyzer, view=fipa_window)
    sys.exit(fipa_app.exec())

if __name__ == "__main__":
    main()
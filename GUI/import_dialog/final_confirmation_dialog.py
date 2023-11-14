from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFileDialog, QPushButton, QLabel, QRadioButton, QHBoxLayout

class FinalConfirmationDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open File")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.file_path = None
        
        
        self.warning = QLabel('Die Daten wurden importiert. Zum beenden drücken Sie auf "Weiter" ')
        
        layout.addWidget(self.warning)
        self.setLayout(layout)
    
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFileDialog, QPushButton, QLabel, QRadioButton, QHBoxLayout, QWidget
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont

class OpenfileDialog(QDialog):

    chosen_option = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open File")
        
        main_layout = QVBoxLayout()

        center_widget = QWidget()
        layout = QVBoxLayout(center_widget)
        self.setAcceptDrops(True)
        self.drop_label = QLabel("Drop File Here", self)
        self.drop_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24) 
        self.drop_label.setFont(font)
        self.drop_label.setWordWrap(True)
        
        self.file_path = None
        self.chosen_radio_option = "dkbfamilie"  # Initialize with default value

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.open_button = QPushButton("Open File")
        self.open_button.setFont(font)
        self.open_button.setMinimumSize(200, 50)  # Width, Height
        self.open_button.clicked.connect(self.open_file_dialog)
        button_layout.addWidget(self.open_button)
        button_layout.addStretch()

        self.radio_widget = QWidget()
        self.radio_layout = QVBoxLayout(self.radio_widget)
        self.option1_radio = QRadioButton("DKB Familie")
        self.option2_radio = QRadioButton("ING Soeren")
        self.option1_radio.setChecked(True)
        self.radio_layout.addWidget(self.option1_radio)
        self.radio_layout.addWidget(self.option2_radio)
        self.option1_radio.toggled.connect(self.update_chosen_option)
        self.option2_radio.toggled.connect(self.update_chosen_option)

        layout.addLayout(button_layout)
        main_layout.addWidget(center_widget, alignment=Qt.AlignCenter)
        self.or_label = QLabel("or", self)
        self.or_label.setFont(font)
        main_layout.addWidget(self.or_label, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        main_layout.addWidget(self.drop_label, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        main_layout.addStretch()
        main_layout.addWidget(self.radio_widget, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        self.file_path = event.mimeData().urls()[0].toLocalFile()
        self.drop_label.setText(f"File Dropped: {self.file_path}")

    def update_chosen_option(self):
        if self.option1_radio.isChecked():
            self.chosen_radio_option = "dkbfamilie"
        else:
            self.chosen_radio_option = "ingsoeren"

    def open_file_dialog(self):
        file_dialog = QFileDialog(self, "Open File", "", "CSV Files (*.csv)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setOption(QFileDialog.ReadOnly, True)
    
        if file_dialog.exec_():
            self.file_path = file_dialog.selectedFiles()[0]
            self.drop_label.setText(f"File Chosen: {self.file_path}")
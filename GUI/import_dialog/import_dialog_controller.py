from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout,QStackedWidget, QPushButton, QMessageBox
from GUI.import_dialog.openfile_dialog import OpenfileDialog
from GUI.import_dialog.chose_import_dialog import ChoseImportDialog
from GUI.import_dialog.category_dialog import CategoryDialog
from GUI.import_dialog.confirmation_dialog import ConfirmationDialog
from GUI.import_dialog.final_confirmation_dialog import FinalConfirmationDialog
from Import.import_data import ImportAccountData
from Import.import_utils import add_data_to_db, predict_category, predict_category_ml
import traceback
import pandas as pd

class DialogSequenceManager(QDialog):
    def __init__(self):
        super().__init__()
        
        self.resize(1200, 600)
        self.setFixedWidth(1200)
        self.stacked_widget = QStackedWidget()

        self.open_file_dialog = OpenfileDialog(self)
        self.stacked_widget.addWidget(self.open_file_dialog)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stacked_widget)
        
        self.button_layout = QHBoxLayout()
        self.exit_button = QPushButton("Abbruch")
        self.next_button = QPushButton("Next")

        self.exit_button.clicked.connect(self.exit_dialog)
        self.next_button.clicked.connect(self.next_dialog)
        self.button_layout.addWidget(self.exit_button)
        self.button_layout.addWidget(self.next_button)
        
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)
       
    def next_dialog(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index < self.stacked_widget.count():
            self.handle_special_case_next(current_index)
            self.stacked_widget.setCurrentIndex(current_index + 1)

    def handle_special_case_next(self, current_index):
        #die hasattr-Abfragen sind noch vom Versuch, mit Vor- und Zurück-Buttons zu arbeiten. Ist aber zu kompliziert gewesen
        if current_index == 0:
            #Übergang von Import File-Auswahl zu Transaktionen-Auswahl
            if self.open_file_dialog.file_path:
                self.file_path = self.open_file_dialog.file_path
            else:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText("Wähle eine Datei aus")
                msgBox.setWindowTitle("Error")
                msgBox.exec()
                error_traceback = traceback.format_exc()
                print(error_traceback)  # or save it to a log file
            self.account_name = self.open_file_dialog.chosen_radio_option
            try:
                import_data = ImportAccountData(self.file_path, self.account_name)
                self.transactions = import_data.transactions
                self.db_data = import_data.db_data
            except Exception as e:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText(str(e))
                msgBox.setWindowTitle("Error")
                msgBox.exec()
                error_traceback = traceback.format_exc()
                print(error_traceback)  # or save it to a log file
            if not hasattr(self, 'chose_import_dialog'):
                self.chose_import_dialog = ChoseImportDialog(self.transactions, self.db_data)
                self.stacked_widget.addWidget(self.chose_import_dialog)
        elif current_index == 1:
            #Übergang von Auswahl Transaktionen-Dialog zu Kategorie-Dialog
            indices_to_keep = []
            for index, checkbox in enumerate(self.chose_import_dialog.checkboxes):
                if checkbox.isChecked():
                    indices_to_keep.append(index)
            self.transactions = self.transactions.loc[indices_to_keep, :]
            self.transactions.reset_index(drop=True, inplace=True)
            self.transactions['Buchungsdatum'] = pd.to_datetime(self.transactions['Buchungsdatum'], format='%Y-%m-%d', errors='raise')
            #Hier wird eine Kopie der Instanz-Variable übergeben, damit Original unverändert bleibt:
            predictions = predict_category_ml(self.transactions.copy())
            if not hasattr(self, 'category_dialog'):
                self.category_dialog = CategoryDialog(self.transactions, predictions)
                self.stacked_widget.addWidget(self.category_dialog)
        elif current_index == 2:
            for index, combo_box in enumerate(self.category_dialog.combo_boxes):
                chosen_category = combo_box.currentData()
                self.transactions.loc[index, 'Kategorie'] = chosen_category
            self.transactions =self.transactions.drop(columns=['Zeitschwelle', "Unique"])
            self.transactions['Buchungsdatum'] = self.transactions['Buchungsdatum'].dt.strftime('%Y-%m-%d')
            if not hasattr(self, 'confirmation_dialog'):
                self.confirmation_dialog = ConfirmationDialog()
                self.stacked_widget.addWidget(self.confirmation_dialog)
        elif current_index == 3:
            add_data_to_db(self.account_name, self.transactions)
            if not hasattr(self, 'final_confirmation_dialog'):
                self.confirmation_dialog = FinalConfirmationDialog()
                self.stacked_widget.addWidget(self.confirmation_dialog)
        elif current_index == 4:
            self.exit_dialog()

    def clear_variables(self):
        self.transactions=None
        self.db_data = None
        self.file_path = None
        self.chose_import_dialog = None

    def exit_dialog(self):
        self.clear_variables()
        self.close()
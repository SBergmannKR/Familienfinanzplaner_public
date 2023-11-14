from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGridLayout, QScrollArea, QWidget, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd
class ChoseImportDialog(QDialog):

    def __init__(self, data_frame, data_frame2, parent=None):
        super().__init__(parent)
        main_layout = QGridLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.checkboxes = []  # To keep track of all ComboBoxes

        scroll_area = QScrollArea()
        scroll_content = QWidget()
        layout = QGridLayout(scroll_content)

        data_frame = data_frame[['Buchungsdatum', 'Empfaenger', 'Betrag', 'Zeitschwelle', 'Unique']]
        # Spaltenüberschriften setzen
        for col_index, col_name in enumerate(data_frame.columns):
            label = QLabel(col_name)
            label.setMaximumWidth(200)
            layout.addWidget(label, 0, col_index)
        
        # Ein Platzhalter für die ComboBox-Spalte
        layout.addWidget(QLabel("Kategorie"), 0, len(data_frame.columns))

        # Durchlaufen jeder Zeile im DataFrame
        for row_index, row in data_frame.iterrows():
            # Durchlaufen jeder Spalte in der Zeile
            for col_index, item in enumerate(row):
                label = QLabel(str(item))
                label.setMaximumWidth(200)
                layout.addWidget(label, row_index + 1, col_index)
            checkbox = QCheckBox()
            self.checkboxes.append(checkbox)
            if row['Zeitschwelle'] and row['Unique']:
                checkbox.setChecked(True)
            layout.addWidget(checkbox, row_index + 1, len(data_frame.columns))

        # ScrollArea Setup
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)

        ###### db_data for comparison
        data_frame2 = data_frame2[['Buchungsdatum', 'Empfaenger', 'Betrag']].copy()
        data_frame2['Buchungsdatum'] = pd.to_datetime(data_frame2['Buchungsdatum'])
        #data_frame2.sort_values(by='Buchungsdatum')
        data_frame2 = data_frame2.sort_values('Buchungsdatum', ascending=False)
        data_frame2['Buchungsdatum'] = data_frame2['Buchungsdatum'].dt.strftime('%Y-%m-%d')
        data_frame2 = data_frame2.head(100)
        data_frame2.reset_index(drop=True, inplace=True)
        
        scroll_area2 = QScrollArea()
        scroll_content2 = QWidget()
        layout2 = QGridLayout(scroll_content2)

        # Spaltenüberschriften setzen
        for col_index, col_name in enumerate(data_frame2.columns):
            label = QLabel(col_name)
            label.setMaximumWidth(200)
            layout2.addWidget(label, 0, col_index)

        for row_index, row in data_frame2.iterrows():
            # Durchlaufen jeder Spalte in der Zeile
            for col_index, item in enumerate(row):
                label = QLabel(str(item))
                label.setMaximumWidth(200)
                layout2.addWidget(label, row_index + 1, col_index)
        # ScrollArea Setup
        scroll_area2.setWidget(scroll_content2)
        scroll_area2.setWidgetResizable(True)
        # Hauptlayout

        db_data_label = QLabel("Bestehender Datensatz")
        new_data_label = QLabel("Neuer Datensatz")
        font = QFont()
        font.setPointSize(24) 
        db_data_label.setFont(font)
        new_data_label.setFont(font)
        main_layout.addWidget(db_data_label, 0,0)
        main_layout.addWidget(new_data_label, 0,1)
        main_layout.addWidget(scroll_area2, 1,0)
        main_layout.addWidget(scroll_area, 1,1)
        self.setLayout(main_layout)

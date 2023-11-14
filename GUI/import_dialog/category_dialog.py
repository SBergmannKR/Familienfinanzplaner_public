from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGridLayout, QScrollArea, QWidget
from PySide6.QtCore import Qt
import pandas as pd
from sqlalchemy import create_engine
import sys
sys.path.append('/Users/sorenbergmann/Documents/20_Programmierprojekte/Familienfinanzplaner')
from config import Config

class CategoryDialog(QDialog):

    def __init__(self, data_frame, predictions, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        
        self.combo_boxes = [] # Liste der ComboBoxen, um die Auswahl zu speichern
        
        # ScrollArea Setup
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        layout = QGridLayout(scroll_content)
        layout.setAlignment(Qt.AlignTop)
        
        kategorie_series = pd.Series(predictions)
        data_frame = data_frame[['Buchungsdatum', 'Empfaenger', "Verwendungszweck",'Betrag']]
        column_widths = {'Buchungsdatum': 120, 'Empfaenger': 200, 'Verwendungszweck': 250, 'Betrag': 100, 'Kategorie': 150}
        
        # Spaltenüberschriften setzen
        for col_index, col_name in enumerate(data_frame.columns):
            label = QLabel(col_name)
            label.setFixedWidth(column_widths[col_name])
            layout.addWidget(label, 0, col_index)
        
        # Ein Platzhalter für die ComboBox-Spalte
        label = QLabel("Kategorie")
        label.setFixedWidth(column_widths['Kategorie'])
        layout.addWidget(label, 0, len(data_frame.columns))

        # Durchlaufen jeder Zeile im DataFrame
        for row_index, row in data_frame.iterrows():
            kategorie_value = kategorie_series.iloc[row_index]
            # Durchlaufen jeder Spalte in der Zeile
            for col_index, item in enumerate(row):
                label = QLabel(str(item))
                label.setFixedWidth(column_widths[data_frame.columns[col_index]])
                layout.addWidget(label, row_index + 1, col_index)
            
            combo_box = QComboBox()
            
            db_path = Config.SQLALCHEMY_DATABASE_URI
            engine = create_engine(f'sqlite:///{db_path}')
            query = 'SELECT [Index], Kategorie FROM kategorien'
            combolist_df = pd.read_sql_query(query, engine)
            categories_list = combolist_df['Kategorie'].tolist()

            # Hinzufügen der Liste zur ComboBox
            for combolist_index, combolist_row in combolist_df.iterrows():
                combo_box.addItem(combolist_row['Kategorie'], combolist_row['Index'])
            self.combo_boxes.append(combo_box)
        
            if not pd.isna(kategorie_value):
                combo_box.setCurrentIndex(int(kategorie_value))
            layout.addWidget(combo_box, row_index + 1, len(data_frame.columns))


        # ScrollArea Setup
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)

        # Hauptlayout
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

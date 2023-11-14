from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget,
    QComboBox,
    QLabel,
    QGroupBox,
    QWidgetAction,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QSpacerItem, 
    QSizePolicy
)
import pandas as pd

from Charts.pie_chart import PieChart
from Charts.bar_chart import MatplotlibBarGraph
from Charts.line_chart import MatplotlibLineGraph

WINDOW_SIZE = 400


class FiPaMainWindow(QMainWindow):
    """Finanzplaner's main window (GUI or view)."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finanzplaner")
        self.setFixedSize(3 * WINDOW_SIZE, 2 * WINDOW_SIZE)
        self.general_layout = QGridLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(self.general_layout)
        self.setCentralWidget(central_widget)

        # Erstellen der Menüleiste
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        self.import_action = QWidgetAction(self)
        self.import_action.setText("Import Data")
        file_menu.addAction(self.import_action)

        # Erstellen der Subframes
        self._create_account_subframe()
        self._create_barplot_subframe()
        self._create_category_subframe()
        #self.general_layout.addWidget(self.sub_frame_category, 4, 0)
        self.sub_frame_category.hide()
        self._create_statistics_subframe()
        self._create_pieplot_subframe()
        self._categorytable_subframe()
        self.line_chart = MatplotlibLineGraph()
        self.trans_scroll_area = QScrollArea()
        
        
        tab_widget = QTabWidget()
        # Erster Reiter
        tab1 = QWidget()
        tab1_layout = QGridLayout()
        tab1_layout.addWidget(self.barplot_subframe, 0,1, 2,1)
        tab1_layout.addWidget(self.sub_frame_stat, 0,2, 2, 1)
        tab1_layout.addWidget(self.pieplot_subframe, 2, 1, 2, 1)
        tab1_layout.addWidget(self.categorytable_subframe, 2,2, 2,1)
        tab1.setLayout(tab1_layout)
        # Zweiter Reiter
        tab2 = QWidget()
        tab2_layout = QGridLayout()
        tab2_layout.addWidget(self.line_chart, 0, 0)
        tab2.setLayout(tab2_layout)
        #Dritter Reiter
        tab3 = QWidget()
        tab3_layout = QGridLayout()
        tab3_layout.addWidget(self.trans_scroll_area)
        tab3.setLayout(tab3_layout)
        # Reiter zum Tab-Widget hinzufügen
        tab_widget.addTab(tab1, 'Übersicht')
        tab_widget.addTab(tab2, 'Kontosaldo')
        tab_widget.addTab(tab3, 'Transaktionen')
        
        # Tab-Widget und andere Widgets zum Hauptlayout hinzufügen
        self.general_layout.addWidget(self.sub_frame_main, 0, 0)
        self.general_layout.addWidget(tab_widget, 0,1, 4, 1)

    def _create_account_subframe(self):
        # Erstellen des Subframes
        self.sub_frame_main = QGroupBox(self)
        self.sub_frame_main.setTitle("Kontoeinstellungen")  # Set the title for the group box
        self.sub_frame_main_layout = QGridLayout()
        self.sub_frame_main.setLayout(self.sub_frame_main_layout)
        self.account_label = QLabel()
        self.account_label.setText('Konto:')
        self.begin_label = QLabel()
        self.begin_label.setText('Beginn:')
        self.end_label = QLabel()
        self.end_label.setText('Ende:')
        self.sub_frame_main_layout.addWidget(self.account_label, 0, 0)
        self.sub_frame_main_layout.addWidget(self.begin_label, 1, 0)
        self.sub_frame_main_layout.addWidget(self.end_label, 2, 0)
        self.attribute_combo_box_account = QComboBox()
        self.attribute_combo_box_account.addItems(["dkbfamilie", "ingsoeren"])
        self.attribute_combo_box_date_begin = QComboBox()
        self.attribute_combo_box_date_begin.addItems(["01-2023"])
        self.attribute_combo_box_date_end = QComboBox()
        self.attribute_combo_box_date_end.addItems(["06-2023"])
        self.sub_frame_main_layout.addWidget(self.attribute_combo_box_account, 0, 1)
        self.sub_frame_main_layout.addWidget(self.attribute_combo_box_date_begin, 1, 1)
        self.sub_frame_main_layout.addWidget(self.attribute_combo_box_date_end, 2, 1)
    
    def _create_barplot_subframe(self):
        self.barplot_subframe = QGroupBox(self)
        self.barplot_subframe.setTitle("Monatsbilanzen")  # Set the title for the group box
        self.barplot_subframe_layout = QGridLayout()
        self.barplot_subframe.setLayout(self.barplot_subframe_layout)
        self.barplot = MatplotlibBarGraph()
        self.barplot_subframe_layout.addWidget(self.barplot)

    def _create_pieplot_subframe(self):
        self.pieplot_subframe = QGroupBox(self)
        self.pieplot_subframe.setTitle("Ausgaben nach Kategorien")  # Set the title for the group box
        self.pieplot_subframe_layout = QGridLayout()
        self.pieplot_subframe.setLayout(self.pieplot_subframe_layout)
        self.pieplot = PieChart()
        self.pieplot_subframe_layout.addWidget(self.pieplot)

    def _categorytable_subframe(self):
        self.categorytable_subframe = QGroupBox(self)
        self.categorytable_subframe.setTitle("Ausgaben nach Kategorien")  # Set the title for the group box
        self.categorytable_subframe_layout = QGridLayout()
        self.categorytable_subframe.setLayout(self.categorytable_subframe_layout)
        self.cat_scroll_area = QScrollArea()
        self.categorytable_subframe_layout.addWidget(self.cat_scroll_area)

    def _create_statistics_subframe(self):
        self.sub_frame_stat = QGroupBox(self)
        self.sub_frame_stat.setTitle("Statistiken")
        self.sub_frame_stat_layout = QGridLayout()
        self.sub_frame_stat.setLayout(self.sub_frame_stat_layout)
        self.labellist = []  # To keep track of all ComboBoxes
        labels = [
            ('Zeitraum:', 'Platzhalter'),
            ('Bilanzsumme:', 'Platzhalter'),
            ('Avg Summe (Monat):', 'Platzhalter'),
            ('Max. Plus:', 'Platzhalter'),
            ('Max. Minus', 'Platzhalter')
        ]
        
        for i, (label_text, result_text) in enumerate(labels):
            label = self.create_label(label_text)
            result_label = self.create_label(result_text)
            self.sub_frame_stat_layout.addWidget(label, i, 0)
            self.sub_frame_stat_layout.addWidget(result_label, i, 1)
            self.labellist.append(result_label)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sub_frame_stat_layout.addItem(spacer, len(labels), 0, 1, 2)

    def _create_transaction_view(self, content):
        scroll_content = QWidget()
        layout = QGridLayout(scroll_content)
        layout.setAlignment(Qt.AlignTop)
        content = content[['Buchungsdatum', 'Empfaenger', 'Betrag', "Kategorie", "Saldo"]]

        # Spaltenüberschriften setzen
        for col_index, col_name in enumerate(content.columns):
            label = QLabel(col_name)
            layout.addWidget(label, 0, col_index)

        # Durchlaufen jeder Zeile im DataFrame
        for row_index, row in content.iterrows():
            # Durchlaufen jeder Spalte in der Zeile
            for col_index, item in enumerate(row):
                if content.columns[col_index] == 'Buchungsdatum':
                    item = pd.to_datetime(str(item)).strftime('%Y-%m-%d')
                elif content.columns[col_index] in ['Betrag', 'Saldo']:
                    item = "{:.2f}".format(item)  # Formatieren auf zwei Dezimalstellen
                label = QLabel(str(item))
                if content.columns[col_index] == 'Empfaenger':
                    label.setFixedWidth(300)  # Setzen der gewünschten Breite
                elif content.columns[col_index] in ['Buchungsdatum', 'Betrag', 'Saldo']:
                    label.setFixedWidth(90) 
                
                layout.addWidget(label, row_index + 1, col_index)

        # ScrollArea Setup
        self.trans_scroll_area.setWidget(scroll_content)
        self.trans_scroll_area.setWidgetResizable(True)

    def _create_category_labels_in_scroll_area(self, content):
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout()

        # Setzen der Schriftart für Header
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        # Hinzufügen der Header Labels
        for col_index, col_name in enumerate(content.columns):
            header_label = QLabel(col_name)
            header_label.setFont(header_font)
            self.scroll_layout.addWidget(header_label, 0, col_index)

        # Durchlaufen jeder Zeile im DataFrame
        for row_index, row in content.iterrows():
            # Durchlaufen jeder Spalte in der Zeile
            for col_index, item in enumerate(row):
                label = QLabel(str(item))
                self.scroll_layout.addWidget(label, row_index + 1, col_index)

        self.scroll_widget.setLayout(self.scroll_layout)
        self.cat_scroll_area.setWidget(self.scroll_widget)
        self.cat_scroll_area.setWidgetResizable(True)

    def _create_category_subframe(self):
        self.sub_frame_category = QGroupBox(self)
        self.sub_frame_category.setTitle("Kategorien")
        self.sub_frame_category_layout = QGridLayout()
        self.sub_frame_category.setLayout(self.sub_frame_category_layout)
        self.category_label = QLabel()
        self.category_label.setText('Kategorie:')
        self.sub_frame_category_layout.addWidget(self.category_label, 0, 0)
        self.attribute_combo_box_category = QComboBox()
        self.sub_frame_category_layout.addWidget(self.attribute_combo_box_category, 0, 1)
        self.ok_button = QPushButton("Generate Results")
        self.sub_frame_category_layout.addWidget(self.ok_button, 1, 0, 1, 2)
    
    def get_date_begin_combo_text(self):
        return self.attribute_combo_box_date_begin.currentText()
    
    def get_date_end_combo_text(self):
        return self.attribute_combo_box_date_end.currentText()
    
    def get_category_combo_text(self):
        return self.attribute_combo_box_category.currentText()
    
    def get_account_combo_text(self):
        return self.attribute_combo_box_account.currentText()
    
    def update_category_combobox(self, categories):
        self.attribute_combo_box_category.clear()
        self.attribute_combo_box_category.addItems(['Alle', 'Alle Ausgaben'])
        self.attribute_combo_box_category.addItems(categories)
    
    def update_date_comboboxes(self, all_dates):

        self.attribute_combo_box_date_begin.clear()
        self.attribute_combo_box_date_end.clear()
        for date in all_dates:
            self.attribute_combo_box_date_begin.addItem(date)
            self.attribute_combo_box_date_end.addItem(date)
    
    def create_label(self, text, font_size=24):
            label = QLabel()
            label.setText(text)
            font = QFont()
            font.setPointSize(font_size)
            label.setFont(font)
            return label

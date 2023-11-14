
from PySide6.QtWidgets import QDialog
import pandas as pd
from pandas.tseries.offsets import MonthBegin, MonthEnd

from config import Config
from GUI.import_dialog.import_dialog_controller import DialogSequenceManager

class FiPaController():
#Link between the GUI-Logic and the back-end-logic. 
#Date conversions are made here. Dates in GUI are always strings, Dates in Backend are Datetime-objects or periods or related object-types. 
#Exceptions are the plots. They get the data as datetime-objects and the reformating is done within the class of the chart.
    def __init__(self, model, view):
        self._evaluate = model
        self._view = view
        self.begin_date = None
        self.end_date = None
        self.updating_combo_box = False
        self.db_path = Config.SQLALCHEMY_DATABASE_URI
        self.analyzer = self._evaluate()
        self.get_data()
        self.perform_updates()
        self.connect_signals_and_slots()

    def get_data(self):
        print("get_data() was called")
        self.account = self._view.get_account_combo_text()
        self.analyzer.get_data(self.account)
        self.update_comboboxes_based_on_account()

    def perform_updates(self):        
        self.update_bar_chart_main()
        self.update_pie_chart()
        self.create_table()
        self.update_statistics()
        self.update_line_chart()
        self.update_transaction_view()
        #self._view.bar_graph_category.plot_bar_from_dataframe(sum_by_month, acc_category)

    def update_bar_chart_main(self):
        sum_by_month, sum_total = self.analyzer.sum_month('Alle')
        self._view.barplot.plot_bar_from_dataframe(sum_by_month, '')

    def create_table(self):
        df = self.analyzer.sum_category()
        df = df.sort_values('Betrag', ascending=True).reset_index(drop=True).round(2)
        self._view._create_category_labels_in_scroll_area(df)

    def update_statistics(self):
        sum_by_month, sum_total = self.analyzer.sum_month('Alle')
        no_month=sum_by_month.shape[0]
        self._view.labellist[0].setText(f'{no_month} Monate')
        self._view.labellist[1].setText(self.format_currency(sum_total))
        self._view.labellist[2].setText(self.format_currency(sum_by_month['Sum'].mean()))
        self._view.labellist[3].setText(self.format_currency(sum_by_month['Sum'].max()))
        self._view.labellist[4].setText(self.format_currency(sum_by_month['Sum'].min()))

    def update_pie_chart(self):
        df_neg = self.analyzer.sum_category()
        df_neg=df_neg[df_neg['Betrag']<0].copy()
        df_neg['Betrag'] = df_neg['Betrag'].abs()
        df_neg = df_neg.sort_values('Betrag', ascending=False)
        top_5_df_neg = df_neg.head(5)
        rest_sum = df_neg.tail(len(df_neg) - 5)['Betrag'].sum()
        new_row = pd.DataFrame({'Kategorie': ['Weiteres'], 'Betrag': [rest_sum]})
        final_df_neg = pd.concat([top_5_df_neg, new_row]).reset_index(drop=True)
        self._view.pieplot.plot_pie(final_df_neg, '')

    def update_line_chart(self):
        saldo = self.analyzer.get_saldo()
        saldo = saldo.sort_values('Buchungsdatum')
        self._view.line_chart.plot_line_from_dataframe(saldo, "Kontostand")
        
    def update_transaction_view(self):
        transactions = self.analyzer.get_transactions_slice()
        transactions = transactions.sort_values('Buchungsdatum', ascending=False).reset_index()
        self._view._create_transaction_view(transactions)

    def show_dialog_sequence(self):
        self.dialog_sequence_manager = DialogSequenceManager()
        self.dialog_sequence_manager.show()

    def set_dates(self):
        if self.updating_combo_box:
            return
        date_begin = self._view.get_date_begin_combo_text()
        date_end = self._view.get_date_end_combo_text()
        if not date_begin or not date_end:
            print("Either begin or end date is empty. Skipping update.")
            return
        else:
            date_begin = pd.to_datetime(date_begin, format="%m-%Y")
            date_begin = pd.Timestamp(date_begin)#.normalize()
            date_end = pd.to_datetime(date_end, format="%m-%Y")
            date_end = pd.Timestamp(date_end).normalize() + MonthEnd(0)

        if date_begin > date_end:
            date_begin, date_end = date_end, date_begin

        self.analyzer.set_date_limits(date_begin, date_end)
        #self._perform_update()

    def combobox_dates_update_action(self):
        self.set_dates()
        self.perform_updates()

    def connect_signals_and_slots(self):
        self._view.attribute_combo_box_account.currentIndexChanged.connect(self.get_data)
        self._view.attribute_combo_box_date_begin.currentIndexChanged.connect(self.combobox_dates_update_action)
        self._view.attribute_combo_box_date_end.currentIndexChanged.connect(self.combobox_dates_update_action)
        self._view.import_action.triggered.connect(self.show_dialog_sequence)

    def update_comboboxes_based_on_account(self):
        #Retrieves the start- and end-dates of the current dataset in datetime-format. Calculates a list of strings with the dates and passes is to the GUI
        self.updating_combo_box = True  # set flag
        date_begin= self.analyzer.begin_date
        date_end = self.analyzer.end_date
        all_dates = pd.date_range(date_begin, date_end, freq='M')
        # Check if end_date's month is in all_dates
        if date_end.month != all_dates[-1].month or date_end.year != all_dates[-1].year:
            all_dates = all_dates.append(pd.DatetimeIndex([date_end.replace(day=1)]))
        # Format the dates as "mm-yyyy" and add them to the comboboxes
        all_dates_str = [date.strftime("%m-%Y") for date in all_dates]
        self._view.update_date_comboboxes(all_dates_str)
        self.updating_combo_box = False  # reset flag

    def format_currency(self, value):
        formated_value = "{:,.2f}€".format(value).replace(",", "x").replace(".", ",").replace("x", ".")
        return formated_value
    
    def date_to_string(self, date):
        string = date.dt.strftime('%m-%Y')
        return string
    
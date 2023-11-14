import pandas as pd
from pandas.tseries.offsets import MonthBegin, MonthEnd
import sys
sys.path.append('/Users/sorenbergmann/Documents/20_Programmierprojekte/Familienfinanzplaner')
from sqlalchemy import create_engine

from config import Config

class TransactionAnalyzer():
    def __init__(self):
        print("__init__TransActionAnalyzer_Called")

    def get_data(self, account):
        self.db_name = Config.SQLALCHEMY_DATABASE_URI
        self.account= account
        self.engine = create_engine(f'sqlite:///{self.db_name}')
        self.sql_query = sql_query = f"""
                SELECT 
                t1.Buchungsdatum, t1.Empfaenger, t1.Verwendungszweck, t1.Betrag, 
                t1.Glaeubiger, t1.Saldo, t2.Kategorie
                FROM {self.account} AS t1
                LEFT JOIN kategorien AS t2 ON t1.Kategorie = t2.[Index]
                """
        self.dfdata = pd.read_sql_query(self.sql_query, self.engine)
        self.dfdata['Buchungsdatum'] = pd.to_datetime(self.dfdata['Buchungsdatum'], format='%Y-%m-%d')
        self.dfdata['Betrag'] = pd.to_numeric(self.dfdata['Betrag'], errors='coerce')
        self.begin_date, self.end_date=self.get_date_limits()
    
    def get_data_ml(self, account):
        self.db_name = Config.SQLALCHEMY_DATABASE_URI
        self.account= account
        self.engine = create_engine(f'sqlite:///{self.db_name}')
        self.sql_query = f"""
                SELECT 
                t1.Buchungsdatum, t1.Empfaenger, t1.Verwendungszweck, t1.Betrag, 
                t1.Glaeubiger, t1.Saldo, t1.Kategorie
                FROM {self.account} AS t1
                """
        self.dfdata = pd.read_sql_query(self.sql_query, self.engine)
        self.dfdata['Buchungsdatum'] = pd.to_datetime(self.dfdata['Buchungsdatum'], format='%Y-%m-%d')
        self.dfdata['Betrag'] = pd.to_numeric(self.dfdata['Betrag'], errors='coerce')
        self.begin_date, self.end_date=self.get_date_limits()

    def set_date_limits(self, begin_date, end_date):
        self.begin_date = begin_date
        self.end_date = end_date

    def _get_mask(self):
        mask = (
            (self.dfdata['Buchungsdatum'] >= self.begin_date) &
            (self.dfdata['Buchungsdatum'] <= self.end_date)
        )
        return mask
    
    def sum_month(self, category):
        # Creating a PeriodIndex that includes all months between the beginning and end dates
        all_months = pd.period_range(self.begin_date, self.end_date, freq='M')
        mask = self._get_mask()
        # Apply the mask based on the category
        if category == 'Alle':
            monthly_sum = self.dfdata[mask].groupby(
                self.dfdata['Buchungsdatum'].dt.to_period('M'))['Betrag'].sum()
        elif category == 'Alle Ausgaben':
            monthly_sum = self.dfdata[
                (self.dfdata['Betrag'] < 0) & mask
            ].groupby(
                self.dfdata['Buchungsdatum'].dt.to_period('M'))['Betrag'].sum()
        else:
            monthly_sum = self.dfdata[
                (self.dfdata['Kategorie'] == category) & mask
            ].groupby(
                self.dfdata['Buchungsdatum'].dt.to_period('M'))['Betrag'].sum()

        # Reindex the Series to include all months between beginning and end dates, and fill missing values with 0
        monthly_sum = monthly_sum.reindex(all_months, fill_value=0)
        monthly_sum_df = monthly_sum.reset_index()
        monthly_sum_df.columns = ['Month', 'Sum']

        return monthly_sum_df, monthly_sum_df['Sum'].sum()
    
    def get_saldo(self):
        mask = self._get_mask()
        saldo=self.dfdata.loc[mask, ['Buchungsdatum', 'Saldo']]
        saldo['Saldo'].fillna(0, inplace=True)
        return saldo
    
    def sum_category(self):
        mask = self._get_mask()
        category_sum = self.dfdata[mask].groupby(
            self.dfdata['Kategorie'])['Betrag'].sum().reset_index()
        months_in_period = self.dfdata[mask]['Buchungsdatum'].dt.month.nunique()
        category_sum['Durchschnitt'] = category_sum['Betrag'] / months_in_period
        return category_sum

    def get_unique_categories(self):
        return self.dfdata['Kategorie'].unique().tolist()
    
    def get_date_limits(self):
        begin_date = pd.Timestamp(self.dfdata['Buchungsdatum'].min())
        end_date = pd.Timestamp(self.dfdata['Buchungsdatum'].max())
        return begin_date, end_date
    
    def get_transactions_slice(self):
        mask = self._get_mask()
        return self.dfdata[mask]
    
    def get_all_transactions(self):
        return self.dfdata

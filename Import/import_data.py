import sys
sys.path.append('/Users/sorenbergmann/Documents/20_Programmierprojekte/Familienfinanzplaner')
import pandas as pd
from sqlalchemy import create_engine
import traceback

from config import Config
from Import.import_utils import check_unique, clean_currency_value, mark_date_column

class ImportAccountData:
    def __init__(self, datafile, account_name):
        self.datafile= datafile
        self.db_path = Config.SQLALCHEMY_DATABASE_URI
        self.account_name = account_name
        self.db_data = self._import_dbdata()
        self.max_date_db_data = self._get_max_date()
        if account_name == 'ingsoeren':
            self.import_ing()
        elif account_name == 'dkbfamilie':
           self.import_dkb()
        else:
            print('Zu diesem Konto sind keine Daten hinterlegt.')

    def common_import_tasks(self):
        self.transactions = mark_date_column(self.transactions, self.max_date_db_data)
        self.transactions['Buchungsdatum'] = self.transactions['Buchungsdatum'].dt.strftime('%Y-%m-%d')
        self.transactions = check_unique(self.db_data, self.transactions)
    
    def import_ing(self):
            self.transactions = pd.read_csv(self.datafile, 
                                   delimiter=';', 
                                   encoding="latin-1",
                                   skiprows=13, 
                                   header=0
                                   )
            self.transactions = self.transactions.drop(columns=['Valuta', 'Buchungstext', 'Währung', 'Währung.1'])
            self.transactions['Kategorie'] = None
            self.transactions['Glaeubiger'] = None
            self.transactions.rename(columns={'Buchung': 'Buchungsdatum', 'Auftraggeber/Empfänger' : 'Empfaenger'}, inplace=True)
            self.transactions['Saldo'] = self.transactions['Saldo'].apply(clean_currency_value)
            self.transactions['Betrag'] = self.transactions['Betrag'].apply(clean_currency_value)
            self.transactions['Buchungsdatum'] = pd.to_datetime(self.transactions['Buchungsdatum'], format="%d.%m.%Y", errors='coerce', dayfirst=False)
            self.common_import_tasks()
        
    def import_dkb(self):
        self.transactions = pd.read_csv(self.datafile, 
                               delimiter=';', 
                               encoding="utf-8",
                               skiprows=4, 
                               header=0,
                               na_values=['']
                               )
        self.transactions = self.transactions[self.transactions['Status'] == "Gebucht"]
        self.transactions.reset_index(drop=True, inplace=True)
        self.transactions = self.transactions.drop(columns=['Wertstellung', 
                                                  'Status', 'Zahlungspflichtige*r', 'Umsatztyp',
                                                  'Mandatsreferenz', 'Kundenreferenz'])
        self.transactions['Kategorie'] = None
        self.transactions['Saldo'] = None
        self.transactions.rename(columns={'Zahlungsempfänger*in': 'Empfaenger', 'Gläubiger-ID' : 'Glaeubiger'}, inplace=True)
        self.transactions['Betrag'] = self.transactions['Betrag'].apply(clean_currency_value)
        self.transactions['Buchungsdatum'] = pd.to_datetime(self.transactions['Buchungsdatum'], format="%d.%m.%y", errors='coerce', dayfirst=False)
        self.common_import_tasks()

    # Importiert die DB-Daten zum Vergleich mit den importierten CSV-Daten
    def _import_dbdata(self):
            engine = create_engine(f'sqlite:///{self.db_path}')
            query = f'SELECT * FROM {self.account_name}'
            df = pd.read_sql_query(query, engine)
            df['Buchungsdatum'] = pd.to_datetime(df['Buchungsdatum'], errors='coerce', dayfirst=False)
            return df
    
    def _get_max_date(self):
        latest_date = self.db_data['Buchungsdatum'].max()
        return latest_date



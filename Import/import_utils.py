import pandas as pd
from sqlalchemy import Table, create_engine, func, select, MetaData
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append('/Users/sorenbergmann/Documents/20_Programmierprojekte/Familienfinanzplaner')

from config import Config

def check_unique(db_data, check_transactions, report=False):
        mask = check_transactions.set_index(['Buchungsdatum', 'Empfaenger', 'Betrag']).index.isin(
            db_data.set_index(['Buchungsdatum', 'Empfaenger', 'Betrag']).index
            )
        check_transactions['Unique'] = ~mask

        unique_in_check = check_transactions[~mask]
        duplicates = check_transactions[mask]
        if report == True:
            print(f'Anzahl der zu prüfenden transactions: {check_transactions.shape[0]}')
            print(f'Anzahl der Reihen der aus der db importieren Originaldaten: {db_data.shape[0]}')
            print(f'Anzahl der Reihen der Uniquen Items im check_transactions-df (Richtig: 94):{unique_in_check.shape[0]}')
        else:
             pass
        return check_transactions

def add_data_to_db(account_name, transactions):
    db_path = Config.SQLALCHEMY_DATABASE_URI
    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    if account_name == 'ingsoeren':
        tablename = 'ingsoeren'
    elif account_name == 'dkbfamilie':
        tablename = 'dkbfamilie'
    else:
        print('Zu diesem Konto sind keine Daten hinterlegt.')
        return

    # Erstellen eines Table-Objekts für die SQL-Alchemy Abfrage
    table = Table(tablename, metadata, autoload_with=engine)

    # Ermitteln des höchsten Index in der vorhandenen Tabelle
    max_index_query = select(func.max(table.c.Index))  # Korrekter Spaltenname
    max_index_result = session.execute(max_index_query)
    max_index = max_index_result.scalar() or 0

    # Sortieren der Transaktionen vom ältesten zum neuesten Datum
    transactions = transactions.sort_values(by='Buchungsdatum')

    # Hinzufügen des fortlaufenden Index zu den neuen Transaktionen
    transactions['Index'] = range(max_index + 1, max_index + 1 + len(transactions))

    # Überprüfen, ob die Saldo-Spalte leer ist
    if transactions['Saldo'].isna().any():
        # Abrufen des letzten Saldos aus der Datenbank
        last_balance_query = select(table.c.Saldo).order_by(table.c.Buchungsdatum.desc()).limit(1)
        last_balance_result = session.execute(last_balance_query)
        last_balance = last_balance_result.scalar() or 0

        # Aktualisieren des Saldos in transactions
        current_balance = last_balance
        for index, row in transactions.iterrows():
            current_balance += row['Betrag']
            transactions.at[index, 'Saldo'] = current_balance

    # Daten in die Datenbank einfügen
    #print(transactions[["Index", "Buchungsdatum", "Betrag", "Saldo"]])
    transactions.to_sql(tablename, con=engine, if_exists="append", index=False)

    # Schließen der Session
    session.close()

def clean_currency_value(value):
        value = value.replace('.', '')      # Remove the thousands separator
        value = value.replace(',', '.')     # Replace comma with a dot
        value = value.replace('€', '')      # Remove euro sign
        value = value.encode('utf-8').decode('ascii', 'ignore') # Remove non-ASCII characters
        return float(value.strip())         # Convert to float

def mark_date_column(df, date):
        df['Zeitschwelle'] = df['Buchungsdatum'] > date
        return df

def predict_category_ml(transactions):
    #import erst an dieser Stelle um Zirkelbezug zu unterbinden
    from Import.auto_categorize import run_model
    predictions = run_model(transactions)
    return predictions

def assign_prediction_value(row):
    #Nicht mehr in aktiver benuztung, da die ML-Lösung besser funktioniert
    empfaenger = row['Empfaenger']
    verwendungszweck = row['Verwendungszweck']
    
    category_keywords = {
        21: ['rewe', 'aldi', 'bio', 'netto', 'edeka', 'denn?s', 'steinecke', 'alnatura', 'kutzner', 'brotmeisterei', 'heidebrot', 'brotmeisterei', 'kamps//berlin/de'],
        4: ['budni', "rossmann", "dm"],
        17: ['honegger'],
        14: ['spotify', 'apple', 'disney+'],
        26: ['ernst'],
        16: ['thk', 'marten'],
        10: ['apotheke'],
        3: ['monatsgeld'],
        13: ['familienkasse'],
        8: ['berlin energie', 'joule'],
        5: ['schonau']
    }
    
    if empfaenger is not None and verwendungszweck is not None:
        empfaenger_words = set(empfaenger.lower().split())
        verwendungszweck_words = set(verwendungszweck.lower().split())
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in empfaenger_words or keyword in verwendungszweck_words:
                    return category
                
    return None


def predict_category(transactions):
    transactions['Kategorie'] = transactions.apply(assign_prediction_value, axis=1)
    return transactions



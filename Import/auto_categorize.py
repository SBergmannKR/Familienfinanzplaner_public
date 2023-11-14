import os
import pandas as pd
import Model.class_analysis as ca 
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle


def prepare_data_tf_idf(features, state):
    # Vorbereiten der Daten für die TF-IDF-Transformation
    script_dir = os.path.dirname(__file__)  # Verzeichnis des aktuellen Skripts
    tf_idf_model_path = os.path.join(script_dir, 'ml_files/tfidf_vectorizer.pkl')  # Absoluter Pfad zur clf_model.pkl
    features['Year'] = features['Buchungsdatum'].dt.year
    features['Month'] = features['Buchungsdatum'].dt.month
    features['Day'] = features['Buchungsdatum'].dt.day
    features['Empfaenger'] = features['Empfaenger'].fillna('').str.lower()
    features['Verwendungszweck'] = features['Verwendungszweck'].fillna('').str.lower()

    # Kombinieren der Textfelder
    features['combined_text'] = features['Empfaenger'] + ' ' + features['Verwendungszweck']

    # TF-IDF-Transformation
    vectorizer = TfidfVectorizer()
    if state == "training":
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(features['combined_text'])
        with open(tf_idf_model_path, 'wb') as file:
            pickle.dump(vectorizer, file)
        feature_names = vectorizer.get_feature_names_out()
    else:
        with open(tf_idf_model_path, 'rb') as file:
            loaded_tfidf_vectorizer = pickle.load(file)
        tfidf_matrix = loaded_tfidf_vectorizer.transform(features['combined_text'])
        feature_names = loaded_tfidf_vectorizer.get_feature_names_out()

    # TF-IDF-Matrix in DataFrame umwandeln
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    # Mit ursprünglichen numerischen Features kombinieren
    final_df = pd.concat([features[['Year', 'Month', 'Day', 'Betrag', 'Kategorie']], tfidf_df], axis=1)
    return final_df

def run_model(features):
    # Laden des Modells und der Skalierung
    script_dir = os.path.dirname(__file__)  # Verzeichnis des aktuellen Skripts
    clf_model_path = os.path.join(script_dir, 'ml_files/clf_model.pkl')  # Absoluter Pfad zur clf_model.pkl
    scaler_path = os.path.join(script_dir, 'ml_files/scaler.pkl')  # Absoluter Pfad zur scaler.pkl
    
    with open(clf_model_path, 'rb') as file:
        loaded_clf = pickle.load(file)
    with open(scaler_path, 'rb') as file:
        loaded_scaler = pickle.load(file)
    data_prepared = prepare_data_tf_idf(features, 'application').drop('Kategorie', axis=1)
    data_prepared.fillna(0, inplace=True)
    data_prepared = loaded_scaler.transform(data_prepared)  # Skalierung 
    predictions = loaded_clf.predict(data_prepared)
    if len(predictions) == len(features):
        features['Kategorie'] = predictions
    else:
        print("Length mismatch between predictions and features.")
    return predictions

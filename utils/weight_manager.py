import os
import pandas as pd

WEIGHT_FILE = 'data/weight_records.csv'

def init_weight_file():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(WEIGHT_FILE):
        df = pd.DataFrame(columns=['username', 'date', 'weight'])
        df.to_csv(WEIGHT_FILE, index=False)

def load_weight_records():
    init_weight_file()
    return pd.read_csv(WEIGHT_FILE)

def save_weight_record(username, date, weight):
    df = load_weight_records()
    
    # Eliminar registro existente si lo hay para esa fecha y usuario
    df = df[~((df['username'] == username) & (df['date'] == date))]
    
    # Agregar nuevo registro
    new_record = pd.DataFrame({
        'username': [username],
        'date': [date],
        'weight': [weight]
    })
    
    df = pd.concat([df, new_record], ignore_index=True)
    df.to_csv(WEIGHT_FILE, index=False) 
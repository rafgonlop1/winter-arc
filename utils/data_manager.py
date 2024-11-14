import os
from datetime import datetime, timedelta

import pandas as pd

DATA_FILE = 'data/registros.csv'


def cargar_datos():
    if not os.path.exists('data'):
        os.makedirs('data')

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            'Usuario',
            'Fecha',
            'Actividad Física',
            'Dieta y Nutrición',
            'Descanso o Recuperación',
            'Desarrollo Personal',
            'Puntos'
        ])
        df.to_csv(DATA_FILE, index=False)
        return df

    return pd.read_csv(DATA_FILE)


def guardar_datos(df):
    df.to_csv(DATA_FILE, index=False)


def get_week_dates():
    today = datetime.now()
    return [(today - timedelta(days=x)).strftime('%Y-%m-%d')
            for x in range(6, -1, -1)]


def asignar_rango(puntos):
    if puntos >= 120:
        return "👑 Hokage"
    elif puntos >= 111:
        return "🏆 Sannin Legendario"
    elif puntos >= 91:
        return "⚔️ Jounin"
    elif puntos >= 61:
        return "🎯 Chunin"
    elif puntos >= 31:
        return "🥋 Genin"
    else:
        return "👨‍🎓 Estudiante de la Academia"

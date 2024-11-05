import pandas as pd
import os

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
    """Obtiene las fechas de la semana actual"""
    today = pd.Timestamp.today()
    week_start = today - pd.Timedelta(days=today.dayofweek)
    dates = [(week_start + pd.Timedelta(days=x)).strftime('%Y-%m-%d') 
            for x in range(7)]
    return dates

def asignar_rango(puntos):
    """
    Asigna un rango ninja basado en los puntos mensuales
    
    Rangos:
    - Estudiante de la Academia (0-30): Participación ocasional
    - Genin (31-60): Participación moderada y constante
    - Chunin (61-90): Compromiso sólido, 2-3 actividades diarias
    - Jounin (91-110): Alto nivel de disciplina
    - Sannin Legendario (111-119): Élite, casi perfección
    - Hokage (120): Perfección absoluta
    """
    if puntos <= 30:
        return "Estudiante de la Academia"
    elif puntos <= 60:
        return "Genin"
    elif puntos <= 90:
        return "Chunin"
    elif puntos <= 110:
        return "Jounin"
    elif puntos < 120:
        return "Sannin Legendario"
    else:
        return "Hokage"
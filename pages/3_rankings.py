import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

from utils.data_manager import cargar_datos, asignar_rango
from utils.user_manager import get_users

def get_users_with_gaps(df):
    """
    Identifica usuarios que tienen días sin registros entre su primer y último registro
    """
    users_with_gaps = []
    
    # Obtener la fecha más reciente de todos los registros
    latest_date = df['Fecha'].max()
    
    # Analizar cada usuario
    for username in df['Usuario'].unique():
        user_records = df[df['Usuario'] == username]
        first_date = user_records['Fecha'].min()
        last_date = user_records['Fecha'].max()
        
        # Crear un rango de fechas desde el primer registro hasta el último
        date_range = pd.date_range(start=first_date, end=last_date)
        
        # Obtener las fechas en las que el usuario tiene registros
        user_dates = set(user_records['Fecha'].dt.date)
        
        # Encontrar días faltantes
        missing_dates = [d.date() for d in date_range if d.date() not in user_dates]
        
        if missing_dates:
            users_with_gaps.append({
                'username': username,
                'missing_days': len(missing_dates),
                'first_date': first_date.strftime('%Y-%m-%d'),
                'last_date': last_date.strftime('%Y-%m-%d')
            })
    
    return users_with_gaps

def main():
    st.title("🏆 Rankings")

    df = cargar_datos()

    # Obtener el mes actual
    mes_actual = datetime.now().strftime('%Y-%m')

    # Convertir la columna Fecha a datetime y filtrar por mes actual
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%Y-%m')
    df_mes = df[df['Mes'] == mes_actual]

    # Mostrar usuarios con días sin registros
    users_with_gaps = get_users_with_gaps(df)
    if users_with_gaps:
        st.warning("⚠️ Usuarios con días sin registrar:")
        for user in users_with_gaps:
            st.info(
                f"👤 {user['username']} tiene {user['missing_days']} días sin registros "
                f"entre {user['first_date']} y {user['last_date']}"
            )
        st.markdown("---")

    # Calcular puntos totales por usuario para el mes actual
    puntos_usuarios = df_mes.groupby('Usuario')['Puntos'].sum().reset_index()
    puntos_usuarios['Rango'] = puntos_usuarios['Puntos'].apply(asignar_rango)
    puntos_usuarios = puntos_usuarios.sort_values('Puntos', ascending=False)

    # Mostrar tabla de rankings
    st.header(f"🎯 Tabla de Rankings - {datetime.now().strftime('%B %Y')}")
    st.dataframe(
        puntos_usuarios,
        column_config={
            "Usuario": "Ninja",
            "Puntos": "Puntos del Mes",
            "Rango": "Rango Actual"
        },
        hide_index=True
    )

    if not puntos_usuarios.empty:
        # Gráfico de barras de puntos por usuario
        fig = px.bar(
            puntos_usuarios,
            x='Usuario',
            y='Puntos',
            color='Rango',
            title=f'Puntos por Usuario - {datetime.now().strftime("%B %Y")}',
            labels={'Usuario': 'Ninja', 'Puntos': 'Puntos del Mes'}
        )
        st.plotly_chart(fig)

        # Distribución de rangos
        st.header("📊 Distribución de Rangos")
        fig_pie = px.pie(
            puntos_usuarios,
            names='Rango',
            title='Distribución de Rangos entre Usuarios'
        )
        st.plotly_chart(fig_pie)
    else:
        st.info("No hay registros para este mes")

if __name__ == "__main__":
    main()

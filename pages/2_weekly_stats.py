import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_manager import cargar_datos, get_week_dates

def main():
    st.title("📊 Estadísticas Semanales")
    
    if 'usuario' not in st.session_state or not st.session_state.usuario:
        st.warning("Por favor, ingresa tu nombre de usuario en la página de registro diario")
        return
    
    df = cargar_datos()
    df_usuario = df[df['Usuario'] == st.session_state.usuario]
    
    # Obtener fechas de la semana actual
    fechas_semana = get_week_dates()
    
    # Crear DataFrame con todos los días de la semana
    df_semana = pd.DataFrame({'Fecha': fechas_semana})
    df_puntos = df_usuario[['Fecha', 'Puntos']].copy()
    df_semana = df_semana.merge(df_puntos, on='Fecha', how='left')
    df_semana['Puntos'] = df_semana['Puntos'].fillna(0)
    
    # Gráfico de barras para puntos por día
    fig_barras = px.bar(
        df_semana,
        x='Fecha',
        y='Puntos',
        title='Puntos por Día de la Semana',
        labels={'Fecha': 'Día', 'Puntos': 'Puntos Obtenidos'}
    )
    st.plotly_chart(fig_barras)
    
    # Estadísticas generales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Puntos", df_semana['Puntos'].sum())
    with col2:
        st.metric("Promedio Diario", round(df_semana['Puntos'].mean(), 2))
    with col3:
        st.metric("Mejor Día", df_semana['Puntos'].max())

if __name__ == "__main__":
    main() 
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from utils.data_manager import cargar_datos, asignar_rango

def main():
    st.title("🏆 Rankings")
    
    df = cargar_datos()
    
    # Obtener el mes actual
    mes_actual = datetime.now().strftime('%Y-%m')
    
    # Convertir la columna Fecha a datetime y filtrar por mes actual
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%Y-%m')
    df_mes = df[df['Mes'] == mes_actual]
    
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
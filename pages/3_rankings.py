import streamlit as st
import plotly.express as px
from utils.data_manager import cargar_datos, asignar_rango

def main():
    st.title("🏆 Rankings")
    
    df = cargar_datos()
    
    # Calcular puntos totales por usuario
    puntos_usuarios = df.groupby('Usuario')['Puntos'].sum().reset_index()
    puntos_usuarios['Rango'] = puntos_usuarios['Puntos'].apply(asignar_rango)
    puntos_usuarios = puntos_usuarios.sort_values('Puntos', ascending=False)
    
    # Mostrar tabla de rankings
    st.header("🎯 Tabla de Rankings")
    st.dataframe(
        puntos_usuarios,
        column_config={
            "Usuario": "Ninja",
            "Puntos": "Puntos Totales",
            "Rango": "Rango Actual"
        },
        hide_index=True
    )
    
    # Gráfico de barras de puntos por usuario
    fig = px.bar(
        puntos_usuarios,
        x='Usuario',
        y='Puntos',
        color='Rango',
        title='Puntos por Usuario',
        labels={'Usuario': 'Ninja', 'Puntos': 'Puntos Totales'}
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

if __name__ == "__main__":
    main() 
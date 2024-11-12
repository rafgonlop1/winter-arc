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
                'missing_dates': sorted(missing_dates),  # Añadimos las fechas específicas
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
            with st.expander(f"👤 {user['username']} - {user['missing_days']} días sin registros"):
                st.write("📅 Período:", user['first_date'], "hasta", user['last_date'])
                st.write("📝 Días pendientes de registrar:")
                for date in user['missing_dates']:
                    st.write(f"- {date.strftime('%Y-%m-%d')}")
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
        # Gráfico de barras mejorado con más detalles
        fig = px.bar(
            puntos_usuarios,
            x='Usuario',
            y='Puntos',
            color='Rango',
            title=f'Puntos por Usuario - {datetime.now().strftime("%B %Y")}',
            labels={'Usuario': 'Ninja', 'Puntos': 'Puntos del Mes'},
            text='Puntos',  # Mostrar valores en las barras
            color_discrete_sequence=px.colors.qualitative.Set3  # Paleta de colores más atractiva
        )
        fig.update_traces(textposition='outside')  # Valores fuera de las barras
        st.plotly_chart(fig)

        # Tendencia de puntos acumulados
        st.header("📈 Progreso del Mes")
        
        # Crear un DataFrame con todas las combinaciones de fechas y usuarios
        all_dates = pd.date_range(df_mes['Fecha'].min(), df_mes['Fecha'].max(), freq='D')
        all_users = df_mes['Usuario'].unique()
        date_user_combinations = pd.MultiIndex.from_product(
            [all_dates, all_users], 
            names=['Fecha', 'Usuario']
        )
        
        # Crear DataFrame base con todas las combinaciones
        daily_points = pd.DataFrame(index=date_user_combinations).reset_index()
        
        # Merge con los puntos reales
        points_data = df_mes.groupby(['Fecha', 'Usuario'])['Puntos'].sum().reset_index()
        daily_points = daily_points.merge(
            points_data, 
            on=['Fecha', 'Usuario'], 
            how='left'
        )
        
        # Rellenar NaN con 0
        daily_points['Puntos'] = daily_points['Puntos'].fillna(0)
        
        # Ordenar y calcular acumulados
        daily_points = daily_points.sort_values(['Usuario', 'Fecha'])
        daily_points['Puntos_Acumulados'] = daily_points.groupby('Usuario')['Puntos'].cumsum()
        
        fig_line = px.line(
            daily_points,
            x='Fecha',
            y='Puntos_Acumulados',
            color='Usuario',
            title='Progreso Acumulado del Mes',
            labels={
                'Fecha': 'Día', 
                'Puntos_Acumulados': 'Puntos Acumulados',
                'Usuario': 'Ninja'
            }
        )
        fig_line.update_traces(mode='lines+markers')
        fig_line.update_layout(
            hovermode='x unified',
            yaxis_title="Puntos Totales"
        )
        st.plotly_chart(fig_line)

        # Heatmap de actividad
        st.header("📅 Mapa de Calor - Actividad")
        heatmap_data = df_mes.pivot_table(
            values='Puntos',
            index='Usuario',
            columns=df_mes['Fecha'].dt.strftime('%d'),
            aggfunc='sum',
            fill_value=0
        )
        fig_heat = px.imshow(
            heatmap_data,
            title='Actividad Diaria por Usuario',
            labels=dict(x="Día del Mes", y="Usuario", color="Puntos"),
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_heat)

        # Eliminar el gráfico de pie de distribución de rangos ya que es menos informativo
        
    else:
        st.info("No hay registros para este mes")

if __name__ == "__main__":
    main()

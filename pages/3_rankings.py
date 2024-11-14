from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_manager import cargar_datos, asignar_rango
from utils.weight_manager import load_weight_records


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

    # Rankings por tipo de actividad
    st.header("🎯 Rankings por Actividad")
    actividades = ['Ranking General', 'Actividad Física', 'Dieta y Nutrición', 'Descanso o Recuperación',
                   'Desarrollo Personal']

    # Crear tabs para cada tipo de actividad
    tabs = st.tabs([f"📊 {actividad}" for actividad in actividades])

    # Ranking General
    with tabs[0]:
        st.subheader(f"Ranking General - {datetime.now().strftime('%B %Y')}")
        puntos_usuarios = df_mes.groupby('Usuario')['Puntos'].sum().reset_index()
        puntos_usuarios['Rango'] = puntos_usuarios['Puntos'].apply(asignar_rango)
        puntos_usuarios = puntos_usuarios.sort_values('Puntos', ascending=False)

        st.dataframe(
            puntos_usuarios,
            column_config={
                "Usuario": "Ninja",
                "Puntos": "Puntos del Mes",
                "Rango": "Rango Actual"
            },
            hide_index=True
        )

        # Mover el gráfico general aquí dentro del tab
        if not puntos_usuarios.empty:
            fig = px.bar(
                puntos_usuarios,
                x='Usuario',
                y='Puntos',
                color='Rango',
                title=f'Puntos por Usuario - {datetime.now().strftime("%B %Y")}',
                labels={'Usuario': 'Ninja', 'Puntos': 'Puntos del Mes'},
                text='Puntos',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig)

    # Rankings por actividad
    for tab, actividad in zip(tabs[1:], actividades[1:]):
        with tab:
            # Filtrar datos por actividad y sumar los True
            df_actividad = df_mes.groupby('Usuario')[actividad].sum().reset_index()
            df_actividad = df_actividad.sort_values(actividad, ascending=False)

            # Mostrar tabla de ranking para esta actividad
            st.subheader(f"Ranking - {actividad}")
            st.dataframe(
                df_actividad,
                column_config={
                    "Usuario": "Ninja",
                    actividad: f"Puntos en {actividad}"
                },
                hide_index=True
            )

            # Gráfico de barras para esta actividad
            fig_actividad = px.bar(
                df_actividad,
                x='Usuario',
                y=actividad,
                title=f'Puntos por Usuario en {actividad}',
                labels={'Usuario': 'Ninja', actividad: 'Puntos'},
                text=actividad,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_actividad.update_traces(textposition='outside')
            st.plotly_chart(fig_actividad)

    # Añadir después de los rankings existentes
    st.markdown("---")
    st.header("⚖️ Progreso de Peso Grupal")

    weight_records = load_weight_records()
    if not weight_records.empty:
        weight_records['date'] = pd.to_datetime(weight_records['date'])
        weight_records = weight_records.sort_values('date')  # Ordenar por fecha
        
        # Obtener el primer y último registro de peso para cada usuario
        latest_weights = weight_records.sort_values('date').groupby('username').agg({
            'weight': ['first', 'last'],
            'date': ['first', 'last']
        }).reset_index()
        
        latest_weights.columns = ['username', 'initial_weight', 'current_weight', 'start_date', 'end_date']
        latest_weights['weight_change'] = latest_weights['current_weight'] - latest_weights['initial_weight']
        latest_weights['days_tracked'] = (latest_weights['end_date'] - latest_weights['start_date']).dt.days
        
        # Mostrar tabla de progreso
        st.dataframe(
            latest_weights,
            column_config={
                "username": "Ninja",
                "initial_weight": "Peso Inicial (kg)",
                "current_weight": "Peso Actual (kg)",
                "weight_change": "Cambio (kg)",
                "days_tracked": "Días de Seguimiento"
            },
            hide_index=True
        )
        
        # Gráfico de progreso grupal con fechas ordenadas
        fig = px.line(
            weight_records,
            x='date',
            y='weight',
            color='username',
            title='Progreso de Peso Grupal',
            labels={'date': 'Fecha', 'weight': 'Peso (kg)', 'username': 'Ninja'}
        )
        
        # Configurar el formato de las fechas y asegurar el orden correcto
        fig.update_traces(mode='lines+markers')
        fig.update_xaxes(
            tickformat='%Y-%m-%d',
            tickangle=45,
            type='date',
            tickmode='auto',
            nticks=20
        )
        
        # Mejorar el diseño general del gráfico
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Fecha",
            yaxis_title="Peso (kg)",
            legend_title="Ninja",
            height=500  # Hacer el gráfico un poco más alto para mejor visualización
        )
        
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()

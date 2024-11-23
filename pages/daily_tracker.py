from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from winter.modules.database import get_session, DailyActivity


def daily_tracker():
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        st.error("Por favor, inicia sesión para acceder a esta página.")
        return

    st.title("Daily Tracker")

    # Obtener el user_id de la sesión
    user_id = st.session_state['user_id']  # Asegúrate de almacenar el user_id al autenticarse

    ### Sección: Registro de Actividades Diarias ###

    # Seleccionar fecha
    selected_date = st.date_input("Selecciona una fecha para registrar actividades", value=date.today())

    # Crear sesión de base de datos
    session = get_session()

    # Obtener o crear las actividades del usuario para la fecha seleccionada
    activity = session.query(DailyActivity).filter_by(
        user_id=user_id,
        date=selected_date
    ).first()

    if not activity:
        # Si no existe registro, crear uno nuevo
        activity = DailyActivity(
            user_id=user_id,
            date=selected_date
        )
        session.add(activity)
        session.commit()

    # Casillas de verificación para las actividades
    physical = st.checkbox("🏋️‍♂️ Actividad Física", value=activity.physical_activity, key="physical")
    diet = st.checkbox("🥗 Dieta y Nutrición", value=activity.diet_nutrition, key="diet")
    rest = st.checkbox("😴 Descanso o Recuperación", value=activity.rest_recovery, key="rest")
    personal_dev = st.checkbox("📖 Desarrollo Personal", value=activity.personal_development, key="personal_dev")

    if st.button("Guardar"):
        # Actualizar los valores en la base de datos
        activity.physical_activity = physical
        activity.diet_nutrition = diet
        activity.rest_recovery = rest
        activity.personal_development = personal_dev

        try:
            session.commit()
            st.success("¡Actividades guardadas exitosamente!")
        except SQLAlchemyError as e:
            session.rollback()
            st.error("Error al guardar las actividades.")
            print(f"Error saving activities: {e}")

    ### Sección: Visualización de Actividades ###

    st.markdown("---")  # Línea divisoria

    st.header("Visualización de Actividades Diarias")

    # Obtener fecha inicio y fin de la semana actual
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lunes de la semana actual
    end_of_week = start_of_week + timedelta(days=6)  # Domingo de la semana actual

    # Seleccionar rango de fechas para la visualización
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de inicio",
                                   value=start_of_week,
                                   key="start_date")
    with col2:
        end_date = st.date_input("Fecha de fin",
                                 value=end_of_week,
                                 key="end_date")

    if start_date > end_date:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        session.close()
        return

    # Obtener los datos de actividades del usuario en el rango de fechas seleccionado
    activities = session.query(DailyActivity).filter(
        and_(
            DailyActivity.user_id == user_id,
            DailyActivity.date >= start_date,
            DailyActivity.date <= end_date
        )
    ).all()
    session.close()

    # Crear un DataFrame con todas las fechas en el rango
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    empty_data = {
        'Fecha': [d.date() for d in date_range],
        '🏋️‍♂️ Actividad Física': [False] * len(date_range),
        '🥗 Dieta y Nutrición': [False] * len(date_range),
        '😴 Descanso o Recuperación': [False] * len(date_range),
        '📖 Desarrollo Personal': [False] * len(date_range)
    }
    df = pd.DataFrame(empty_data)

    # Actualizar con los datos existentes
    for activity in activities:
        df.loc[df['Fecha'] == activity.date] = [
            activity.date,
            activity.physical_activity,
            activity.diet_nutrition,
            activity.rest_recovery,
            activity.personal_development
        ]

    # Ordenar el DataFrame por fecha
    df = df.sort_values('Fecha')

    ### Transformación para Visualización Individual de Actividades ###

    # Transformar los datos para mantener cada tipo de actividad
    df_melted = df.melt(id_vars=['Fecha'],
                        value_vars=['🏋️‍♂️ Actividad Física', '🥗 Dieta y Nutrición',
                                    '😴 Descanso o Recuperación', '📖 Desarrollo Personal'],
                        var_name='Actividad',
                        value_name='Realizada')

    # Asignar 1 a actividades realizadas y 0 a las no realizadas
    df_melted['Realizada'] = df_melted['Realizada'].astype(int)

    # Crear el gráfico de barras apiladas que muestra cada actividad por día
    fig = px.bar(
        df_melted,
        x='Fecha',
        y='Realizada',
        color='Actividad',
        title='Actividades Realizadas por Fecha',
        labels={'Realizada': 'Actividades Realizadas'},
        height=500,
        category_orders={'Actividad': ['🏋️‍♂️ Actividad Física', '🥗 Dieta y Nutrición',
                                       '😴 Descanso o Recuperación', '📖 Desarrollo Personal']}
    )

    fig.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Número de Actividades',
        bargap=0.2,
        barmode='group',  # Cambiar a 'stack' si prefieres barras apiladas
        xaxis=dict(
            type='category',  # Forzar el eje X como categorías
            tickformat='%d/%m',  # Formato de fecha simplificado
            tickmode='array',  # Modo de ticks personalizado
            ticktext=[d.strftime('%d/%m') for d in df['Fecha']],  # Texto de los ticks
            tickvals=df['Fecha']  # Valores de los ticks
        )
    )

    st.plotly_chart(fig, use_container_width=True)


daily_tracker()

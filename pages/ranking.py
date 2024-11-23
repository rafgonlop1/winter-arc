from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func, and_, Integer

from winter.modules.database import get_session, DailyActivity, User, WeightEntry
from winter.settings import POINTS_PER_ACTIVITY


def ranking_page():
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        st.error("Por favor, inicia sesión para acceder a esta página.")
        return

    st.title("🏆 Clasificación y Ranking")

    session = get_session()

    RANK_THRESHOLDS = {
        'Estudiante': (0, 30),
        'Genin': (31, 60),
        'Chunin': (61, 90),
        'Jounin': (91, 110),
        'Sannin': (111, 119),
        'Hokage': (120, float('inf'))
    }

    RANK_COLORS = {
        'Estudiante': '#808080',  # Gray
        'Genin': '#90EE90',  # Light Green
        'Chunin': '#4169E1',  # Royal Blue
        'Jounin': '#800080',  # Purple
        'Sannin': '#FFD700',  # Gold
        'Hokage': '#FF4500'  # Red-Orange
    }

    def get_rank(points):
        for rank, (min_pts, max_pts) in RANK_THRESHOLDS.items():
            if min_pts <= points <= max_pts:
                return rank
        return 'Estudiante'

    # Obtener actividades y calcular puntos directamente en la base de datos
    activities_query = session.query(
        User.username,
        DailyActivity.user_id,
        func.sum(func.coalesce(DailyActivity.physical_activity.cast(Integer) * POINTS_PER_ACTIVITY['physical_activity'],
                               0)).label('physical_activity_points'),
        func.sum(
            func.coalesce(DailyActivity.diet_nutrition.cast(Integer) * POINTS_PER_ACTIVITY['diet_nutrition'], 0)).label(
            'diet_nutrition_points'),
        func.sum(
            func.coalesce(DailyActivity.rest_recovery.cast(Integer) * POINTS_PER_ACTIVITY['rest_recovery'], 0)).label(
            'rest_recovery_points'),
        func.sum(func.coalesce(
            DailyActivity.personal_development.cast(Integer) * POINTS_PER_ACTIVITY['personal_development'], 0)).label(
            'personal_development_points'),
    ).join(User).group_by(User.username, DailyActivity.user_id).all()

    # Crear una lista para almacenar los datos de puntos
    leaderboard_data = []
    for row in activities_query:
        total_points = (row.physical_activity_points + row.diet_nutrition_points +
                        row.rest_recovery_points + row.personal_development_points)
        leaderboard_data.append({
            'username': row.username,
            'total_points': total_points,
            'physical_activity': row.physical_activity_points,
            'diet_nutrition': row.diet_nutrition_points,
            'rest_recovery': row.rest_recovery_points,
            'personal_development': row.personal_development_points
        })

    # Crear un DataFrame para la clasificación
    df_leaderboard = pd.DataFrame(leaderboard_data)

    # Si no hay datos, informar al usuario
    if df_leaderboard.empty:
        st.info("No hay datos de actividades disponibles.")
    else:
        ## Clasificación global
        st.subheader("Clasificación Global")
        df_global = df_leaderboard[['username', 'total_points']].sort_values(by='total_points', ascending=False)
        df_global.reset_index(drop=True, inplace=True)
        df_global.index += 1  # Iniciar índice en 1
        df_global['Rango'] = df_global['total_points'].apply(get_rank)
        df_global['Color'] = df_global['Rango'].map(RANK_COLORS)

        fig_global = px.bar(df_global,
                            x='username',
                            y='total_points',
                            text='total_points',
                            color='Rango',
                            color_discrete_map=RANK_COLORS,
                            labels={'username': 'Usuario', 'total_points': 'Puntos Totales'},
                            title='Clasificación Global')
        fig_global.update_traces(texttemplate='%{text} pts<br>%{customdata[0]}',
                                 textposition='outside',
                                 customdata=df_global[['Rango']])

        st.plotly_chart(fig_global, use_container_width=True)

        ## Clasificación por actividad
        st.subheader("Clasificación por Actividad")
        activities = list(POINTS_PER_ACTIVITY.keys())
        activity_labels = {
            'physical_activity': 'Actividad Física',
            'diet_nutrition': 'Dieta y Nutrición',
            'rest_recovery': 'Descanso y Recuperación',
            'personal_development': 'Desarrollo Personal'
        }
        selected_activity = st.selectbox("Selecciona una actividad", activities,
                                         format_func=lambda x: activity_labels[x])

        df_activity = df_leaderboard[['username', selected_activity]].sort_values(by=selected_activity, ascending=False)
        df_activity.reset_index(drop=True, inplace=True)
        df_activity.index += 1  # Iniciar índice en 1
        df_activity['Rango'] = df_activity.index
        df_activity.rename(columns={selected_activity: 'points'}, inplace=True)

        # Gráfico de barras
        fig_activity = px.bar(df_activity, x='username', y='points', text='points',
                              labels={'username': 'Usuario', 'points': 'Puntos'},
                              title=f"Clasificación - {activity_labels[selected_activity]}")
        # Corregir el formato del texto sobre las barras
        fig_activity.update_traces(texttemplate='Posición %{customdata}: %{text} pts', 
                                 textposition='outside',
                                 customdata=df_activity.index)  # Usar el índice como posición
        fig_activity.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        st.plotly_chart(fig_activity, use_container_width=True)

    # Mapa de calor diario
    st.subheader("Mapa de Calor Diario")

    # Calcular primer y último día del mes actual
    today = date.today()
    first_day = date(today.year, today.month, 1)
    if today.month == 12:
        last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)

    start_date = st.date_input("Fecha de inicio", value=first_day)
    end_date = st.date_input("Fecha de fin", value=last_day)

    if start_date > end_date:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
    else:
        # Generar rango de fechas completo
        date_range = pd.date_range(start=start_date, end=end_date)

        # Obtener usuarios
        users = session.query(User).all()
        usernames = {user.id: user.username for user in users}

        # Inicializar DataFrame vacío
        data = []
        for user_id, username in usernames.items():
            for single_date in date_range:
                data.append({
                    'username': username,
                    'date': single_date.date(),
                    'points': 0
                })
        df_heatmap = pd.DataFrame(data)

        # Obtener actividades en el rango de fechas
        activities_in_range = session.query(DailyActivity).filter(
            and_(
                DailyActivity.date >= start_date,
                DailyActivity.date <= end_date
            )
        ).all()

        # Calcular puntos por usuario y fecha
        for activity in activities_in_range:
            daily_points = 0
            for activity_type in POINTS_PER_ACTIVITY.keys():
                if getattr(activity, activity_type):
                    daily_points += POINTS_PER_ACTIVITY[activity_type]
            df_heatmap.loc[
                (df_heatmap['username'] == usernames[activity.user_id]) &
                (df_heatmap['date'] == activity.date), 'points'] = daily_points

        if not df_heatmap.empty:
            df_pivot = df_heatmap.pivot(index='username', columns='date', values='points')
            df_pivot.fillna(0, inplace=True)

            fig = px.imshow(df_pivot,
                            labels=dict(x="Fecha", y="Usuario", color="Puntos"),
                            x=[d.strftime('%d') for d in df_pivot.columns],
                            y=df_pivot.index,
                            aspect="auto",
                            color_continuous_scale='Viridis')

            # Ajustar el eje X para mostrar todas las fechas y añadir título con mes/año
            fig.update_xaxes(type='category')
            fig.update_layout(
                title=f"Actividad diaria - {start_date.strftime('%B %Y')}"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para el rango de fechas seleccionado.")

    # Add weight tracking section before session.close()
    st.subheader("Progreso de Peso del Grupo")

    weight_data = session.query(
        WeightEntry.date,
        WeightEntry.weight,
        User.username
    ).join(User).order_by(WeightEntry.date).all()

    if weight_data:
        df_weight = pd.DataFrame([(w.date, w.weight, w.username) for w in weight_data],
                                 columns=['date', 'weight', 'username'])

        fig_weight = px.line(df_weight,
                             x='date',
                             y='weight',
                             color='username',
                             labels={'date': 'Fecha', 'weight': 'Peso (kg)', 'username': 'Usuario'},
                             title='Progreso de Peso del Grupo')

        st.plotly_chart(fig_weight, use_container_width=True)
    else:
        st.info("No hay datos de peso disponibles.")

    # Agregar versión en el sidebar
    with st.sidebar:
        try:
            import toml
            with open("pyproject.toml", "r") as f:
                project_data = toml.load(f)
                version = project_data["tool"]["poetry"]["version"]
            st.markdown(
                f"<div style='text-align: center; color: rgba(250, 250, 250, 0.4);'>v{version} by @rafaelbenzal96</div>", 
                unsafe_allow_html=True
            )
        except Exception:
            st.markdown(
                "<div style='text-align: center; color: rgba(250, 250, 250, 0.4);'>Version no disponible</div>",
                unsafe_allow_html=True
            )

    session.close()


if __name__ == "__main__":
    ranking_page()

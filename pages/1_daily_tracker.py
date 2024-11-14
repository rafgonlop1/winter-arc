from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_manager import cargar_datos, guardar_datos, get_week_dates


def mostrar_historial(df, usuario, fecha_actual):
    """Muestra el historial de registros recientes y permite modificarlos"""
    st.header("📅 Historial de Registros")

    # Filtrar registros del usuario
    df_usuario = df[df['Usuario'] == usuario].copy()
    df_usuario['Fecha'] = pd.to_datetime(df_usuario['Fecha'])
    df_usuario = df_usuario.sort_values('Fecha', ascending=False)

    # Mostrar los últimos 7 días
    ultimos_registros = df_usuario.head(7).copy()

    if not ultimos_registros.empty:
        # Preparar datos para el gráfico de barras apiladas
        actividades = ['Actividad Física', 'Dieta y Nutrición', 'Descanso o Recuperación', 'Desarrollo Personal']
        ultimos_registros = ultimos_registros.sort_values('Fecha')  # Ordenar cronológicamente

        # Convertir las columnas booleanas a numéricas (0 o 1)
        for actividad in actividades:
            ultimos_registros[actividad] = ultimos_registros[actividad].astype(int)

        # Crear gráfico de barras apiladas
        fig = px.bar(
            ultimos_registros,
            x='Fecha',
            y=actividades,
            title='Actividades Completadas por Día',
            labels={'value': 'Completada', 'variable': 'Actividad'},
            color_discrete_sequence=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']
        )

        # Formatear el eje x para mostrar fechas más legibles
        fig.update_xaxes(tickformat='%d/%m/%Y')
        st.plotly_chart(fig)


def mostrar_estadisticas_semanales(df, usuario):
    """Muestra las estadísticas semanales del usuario"""
    st.header("📊 Estadísticas Semanales")

    df_usuario = df[df['Usuario'] == usuario]

    # Obtener fechas de la semana actual
    fechas_semana = get_week_dates()

    # Crear DataFrame con todos los días de la semana
    df_semana = pd.DataFrame({'Fecha': fechas_semana})
    df_puntos = df_usuario[['Fecha', 'Puntos']].copy()
    df_semana = df_semana.merge(df_puntos, on='Fecha', how='left')
    df_semana['Puntos'] = df_semana['Puntos'].fillna(0)

    # Calcular puntos acumulados
    df_semana['Puntos Acumulados'] = df_semana['Puntos'].cumsum()

    # Crear dos gráficos en columnas
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de barras para puntos por día
        fig_barras = px.bar(
            df_semana,
            x='Fecha',
            y='Puntos',
            title='Puntos por Día',
            labels={'Fecha': 'Día', 'Puntos': 'Puntos Obtenidos'}
        )
        st.plotly_chart(fig_barras)

    with col2:
        # Gráfico de línea para puntos acumulados
        fig_acumulado = px.line(
            df_semana,
            x='Fecha',
            y='Puntos Acumulados',
            title='Puntos Acumulados en la Semana',
            labels={'Fecha': 'Día', 'Puntos Acumulados': 'Puntos Totales'}
        )
        fig_acumulado.add_scatter(
            x=df_semana['Fecha'],
            y=df_semana['Puntos Acumulados'],
            mode='markers',
            showlegend=False
        )
        st.plotly_chart(fig_acumulado)


def main():
    st.title("📝 Registro Diario")

    if 'usuario' not in st.session_state or not st.session_state.usuario:
        st.warning("Por favor, selecciona o crea un usuario en la página principal")
        return

    # Registro de actividades
    fecha = st.date_input("Fecha", datetime.today())
    fecha_str = fecha.strftime("%Y-%m-%d")

    # Cargar datos existentes
    df = cargar_datos()
    registro_existente = df[
        (df['Usuario'] == st.session_state.usuario) &
        (df['Fecha'] == fecha_str)
        ]

    # Establecer valores predeterminados basados en registros existentes
    valores_default = {
        'Actividad Física': False,
        'Dieta y Nutrición': False,
        'Descanso o Recuperación': False,
        'Desarrollo Personal': False
    }

    if not registro_existente.empty:
        for actividad in valores_default.keys():
            valores_default[actividad] = registro_existente.iloc[0][actividad]

    # Mostrar estado actual del día seleccionado
    if not registro_existente.empty:
        st.info(f"Editando registro del {fecha_str}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        actividad_fisica = st.checkbox("Actividad Física 🏋️‍♂️",
                                       value=valores_default['Actividad Física'])
    with col2:
        dieta = st.checkbox("Dieta y Nutrición 🥗",
                            value=valores_default['Dieta y Nutrición'])
    with col3:
        descanso = st.checkbox("Descanso o Recuperación 😴",
                               value=valores_default['Descanso o Recuperación'])
    with col4:
        desarrollo = st.checkbox("Desarrollo Personal 📖",
                                 value=valores_default['Desarrollo Personal'])

    if st.button("Guardar Registro"):
        nueva_entrada = {
            "Usuario": st.session_state.usuario,
            "Fecha": fecha_str,
            "Actividad Física": actividad_fisica,
            "Dieta y Nutrición": dieta,
            "Descanso o Recuperación": descanso,
            "Desarrollo Personal": desarrollo,
            "Puntos": sum([1 for x in [actividad_fisica, dieta, descanso, desarrollo] if x])
        }

        # Eliminar registro existente si lo hay
        df = df[~((df['Usuario'] == st.session_state.usuario) & (df['Fecha'] == fecha_str))]

        # Agregar nuevo registro
        df = pd.concat([df, pd.DataFrame([nueva_entrada])], ignore_index=True)
        guardar_datos(df)
        st.success("Registro guardado exitosamente")
        st.rerun()

    # Mostrar historial y estadísticas
    st.markdown("---")
    mostrar_historial(df, st.session_state.usuario, fecha)
    st.markdown("---")
    mostrar_estadisticas_semanales(df, st.session_state.usuario)


if __name__ == "__main__":
    main()

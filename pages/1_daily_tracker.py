import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

from utils.data_manager import cargar_datos, guardar_datos


def mostrar_historial(df, usuario, fecha_actual):
    """Muestra el historial de registros recientes y permite modificarlos"""
    st.header("📅 Historial de Registros")

    # Filtrar registros del usuario
    df_usuario = df[df['Usuario'] == usuario].copy()
    df_usuario['Fecha'] = pd.to_datetime(df_usuario['Fecha'])
    df_usuario = df_usuario.sort_values('Fecha', ascending=False)

    # Mostrar los últimos 7 días
    ultimos_registros = df_usuario.head(7)

    if not ultimos_registros.empty:
        # Crear una tabla más legible
        tabla_registros = ultimos_registros.copy()
        tabla_registros['Actividades Completadas'] = tabla_registros.apply(
            lambda row: ", ".join([
                "Actividad Física" if row['Actividad Física'] else "",
                "Dieta y Nutrición" if row['Dieta y Nutrición'] else "",
                "Descanso" if row['Descanso o Recuperación'] else "",
                "Desarrollo Personal" if row['Desarrollo Personal'] else ""
            ]).strip(", ") or "Ninguna",
            axis=1
        )

        st.dataframe(
            tabla_registros[['Fecha', 'Actividades Completadas', 'Puntos']],
            column_config={
                "Fecha": "Fecha",
                "Actividades Completadas": "Actividades Completadas",
                "Puntos": "Puntos del Día"
            },
            hide_index=True
        )
    else:
        st.info("Aún no tienes registros")


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

    # Mostrar historial de registros
    st.markdown("---")
    mostrar_historial(df, st.session_state.usuario, fecha)


if __name__ == "__main__":
    main()

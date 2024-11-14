import io
import zipfile
from pathlib import Path

import streamlit as st
import toml

from utils.data_manager import cargar_datos
from utils.settings import APP_CONFIG
from utils.user_manager import get_users, add_user

# Leer versión del pyproject.toml
try:
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    pyproject_data = toml.load(pyproject_path)
    VERSION = pyproject_data["tool"]["poetry"]["version"]
except Exception:
    VERSION = "0.1.0"  # Versión por defecto si no se puede leer el archivo

st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"]
)


def download_data():
    """Función para descargar los datos en formato ZIP"""
    # Crear un buffer en memoria para el ZIP
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Añadir registros.csv
        df_registros = cargar_datos()
        if not df_registros.empty:
            registros_buffer = io.StringIO()
            df_registros.to_csv(registros_buffer, index=False)
            zip_file.writestr('registros.csv', registros_buffer.getvalue())

        # Añadir users.csv
        df_users = get_users()
        if not df_users.empty:
            users_buffer = io.StringIO()
            df_users.to_csv(users_buffer, index=False)
            zip_file.writestr('users.csv', users_buffer.getvalue())

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def user_selector():
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None

    users_df = get_users()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Usuario Existente")
        if not users_df.empty:
            selected_user = st.selectbox(
                "Selecciona tu usuario",
                options=[''] + users_df['username'].tolist()
            )
            if selected_user:
                st.session_state.usuario = selected_user

    with col2:
        st.subheader("Nuevo Usuario")
        new_username = st.text_input("Crear nuevo usuario")
        if st.button("Crear Usuario"):
            if new_username:
                if add_user(new_username):
                    st.session_state.usuario = new_username
                    st.success(f"Usuario {new_username} creado exitosamente!")
                    st.rerun()
                else:
                    st.error("Este nombre de usuario ya existe")


def main():
    st.title("❄️ Winter Arc Tracker")

    # Sidebar con botón de descarga y versión
    with st.sidebar:
        st.title("Opciones")
        zip_data = download_data()
        if zip_data is not None:
            st.download_button(
                label="📥 Descargar Datos",
                data=zip_data,
                file_name="winter_arc_data.zip",
                mime="application/zip",
                help="Descarga todos los registros y usuarios en formato ZIP"
            )
        else:
            st.info("No hay datos disponibles para descargar")

        # Mostrar versión en la parte inferior del sidebar
        st.markdown("---")
        st.caption(f"v{VERSION}")

    user_selector()

    if not st.session_state.usuario:
        st.warning("Por favor, selecciona o crea un usuario para continuar")
        return

    st.success(f"¡Bienvenido, {st.session_state.usuario}! 🎉")

    st.markdown("""
    ### Bienvenido a Winter Arc Tracker
    
    Esta aplicación te ayuda a hacer seguimiento de tu progreso en el Winter Arc.
    
    #### 🎯 Actividades Diarias:
    - 🏋️‍♂️ Actividad Física
    - 🥗 Dieta y Nutrición
    - 😴 Descanso o Recuperación
    - 📖 Desarrollo Personal
    
    #### 🥋 Rangos Ninja Mensuales:
    - 👨‍🎓 Estudiante de la Academia (0-30 puntos/mes)
      *Participación ocasional, ideal para principiantes*
    
    - 🥋 Genin (31-60 puntos/mes)
      *Participación moderada y constante*
    
    - 🎯 Chunin (61-90 puntos/mes)
      *Compromiso sólido, 2-3 actividades diarias*
    
    - ⚔️ Jounin (91-110 puntos/mes)
      *Alto nivel de disciplina y enfoque*
    
    - 🏆 Sannin Legendario (111-119 puntos/mes)
      *Élite, casi perfección*
    
    - 👑 Hokage (120 puntos/mes)
      *Perfección absoluta, todas las actividades todos los días*
    
    Navega por las páginas en la barra lateral para acceder a todas las funcionalidades.
    """)


if __name__ == "__main__":
    main()

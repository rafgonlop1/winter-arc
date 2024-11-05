import streamlit as st
from utils.user_manager import get_users, add_user
from utils.settings import APP_CONFIG
from utils.data_manager import cargar_datos
import pandas as pd
import io

st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"]
)

def download_data():
    """Función para descargar los datos en formato CSV"""
    df = cargar_datos()
    if not df.empty:
        # Crear buffer en memoria para el CSV
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue().decode()
    return None

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
    
    # Sidebar con botón de descarga
    with st.sidebar:
        st.title("Opciones")
        csv_data = download_data()
        if csv_data is not None:
            st.download_button(
                label="📥 Descargar Datos",
                data=csv_data,
                file_name="winter_arc_data.csv",
                mime="text/csv",
                help="Descarga todos los registros en formato CSV"
            )
        else:
            st.info("No hay datos disponibles para descargar")
    
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
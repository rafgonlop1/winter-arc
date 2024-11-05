import streamlit as st
from utils.user_manager import get_users, add_user

st.set_page_config(
    page_title="Winter Arc Tracker",
    page_icon="❄️",
    layout="wide"
)

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
    
    #### 🥋 Rangos Ninja:
    - Estudiante de la Academia (0-30 puntos/mes)
    - Genin (31-60 puntos/mes)
    - Chunin (61-90 puntos/mes)
    - Jounin (91-110 puntos/mes)
    - Sannin Legendario (111+ puntos/mes)
    
    Navega por las páginas en la barra lateral para acceder a todas las funcionalidades.
    """)

if __name__ == "__main__":
    main() 
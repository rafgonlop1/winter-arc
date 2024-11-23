import streamlit as st
from winter.modules.database import verify_credentials, initialize_database, get_user_id, get_user_points
from winter.settings import APP_CONFIG

# Configurar la página
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"]
)

# Inicializar la base de datos al inicio
initialize_database()

# Gestión de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if verify_credentials(username, password):
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = get_user_id(username)
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def main_app():
    st.title("Winter Arc Tracker")

    # Crear dos columnas
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### Bienvenido a Winter Arc Tracker

        Esta aplicación te ayuda a hacer seguimiento de tu progreso en el Winter Arc.
        """)

        # ... resto del contenido de actividades diarias y rangos ...
        st.markdown("""
        #### 🎯 Actividades Diarias:
        - 🏋️‍♂️ Actividad Física
        - 🥗 Dieta y Nutrición
        - 😴 Descanso o Recuperación
        - 📖 Desarrollo Personal
        """)

        st.markdown("""
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
        """)

    with col2:
        st.markdown("""
        ### Tu Rango Actual
        """)
        # Obtener los puntos y rango del usuario
        user_stats = get_user_points(st.session_state['user_id'])
        puntos = user_stats['points']
        rango = user_stats['rank']
        
        st.markdown(f"""
        ### {rango}
        #### Puntos: {puntos}
        """)
        # Barra de progreso (máximo 120 puntos)
        st.progress(min(puntos/120, 1.0))

    st.markdown("Utiliza la barra lateral para navegar entre las diferentes secciones de la aplicación.")

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

if not st.session_state['authenticated']:
    login()
else:
    main_app()
import os

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)

# Configuración de Base de Datos
DB_CONFIG = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB"),
    "admin_login": os.getenv("ADMINISTRATOR_LOGIN"),
    "admin_password": os.getenv("ADMINISTRATOR_LOGIN_PASSWORD")
}
# Construir URL de conexión
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Configuración del Pool de Conexiones
DB_POOL_CONFIG = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800
}

# Configuración SSL
SSL_CONFIG = {
    "sslmode": "require"
}

# Configuración de la Aplicación
APP_CONFIG = {
    "title": "Winter Arc Tracker",
    "icon": "❄️",
    "layout": "wide"
}

POINTS_PER_ACTIVITY = {
    'physical_activity': 1,
    'diet_nutrition': 1,
    'rest_recovery': 1,
    'personal_development': 1
}
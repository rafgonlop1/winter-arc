import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

# Configuración de Base de Datos
DB_CONFIG = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB"),
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

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

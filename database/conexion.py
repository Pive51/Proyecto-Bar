# database/conexion.py
import psycopg2
from config import CONNECTION_STRING

def obtener_conexion():
    try:
        # Ahora conectamos a Supabase en PostgreSQL usando psycopg2 🚀
        conn = psycopg2.connect(CONNECTION_STRING)
        return conn
    except Exception as e:
        print(f"❌ Error crítico al conectar a Supabase (PostgreSQL): {e}")
        return None
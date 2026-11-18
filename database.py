import os
import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    return psycopg2.connect(os.environ.get("DATABASE_URL"), cursor_factory=RealDictCursor, sslmode='require')

def crear_tabla():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT,
            categoria TEXT,
            instagram TEXT,
            foto TEXT
        )
    """)
    # Esto es lo que te faltaba, agrega la columna si tu tabla es vieja
    cursor.execute("ALTER TABLE contactos ADD COLUMN IF NOT EXISTS foto TEXT")
    cursor.execute("ALTER TABLE contactos ADD COLUMN IF NOT EXISTS instagram TEXT")
    cursor.execute("ALTER TABLE contactos ADD COLUMN IF NOT EXISTS categoria TEXT")
    conexion.commit()
    cursor.close()
    conexion.close()

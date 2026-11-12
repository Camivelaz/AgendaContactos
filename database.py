import sqlite3

def obtener_conexion():
    conexion = sqlite3.connect("contactos.db")
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tabla():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT,
            categoria TEXT NOT NULL,
            instagram TEXT,
            foto TEXT
        )
    """)

    columnas = [
        columna[1]
        for columna in cursor.execute(
            "PRAGMA table_info(contactos)"
        ).fetchall()
    ]

    if "instagram" not in columnas:
        cursor.execute(
            "ALTER TABLE contactos ADD COLUMN instagram TEXT"
        )

    if "foto" not in columnas:
        cursor.execute(
            "ALTER TABLE contactos ADD COLUMN foto TEXT"
        )

    conexion.commit()
    conexion.close()
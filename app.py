from flask import Flask, render_template, request, redirect, url_for, flash
from database import obtener_conexion, crear_tabla
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = "agenda_contactos_clave"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}

crear_tabla()

def guardar_foto(archivo):
    if not archivo or archivo.filename == "":
        return None
    nombre_original = secure_filename(archivo.filename)
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else ""
    if extension not in EXTENSIONES_PERMITIDAS:
        return False
    nombre_nuevo = str(uuid.uuid4()) + "." + extension
    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_nuevo)
    archivo.save(ruta)
    return nombre_nuevo

def borrar_foto(nombre):
    if nombre:
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)
        if os.path.exists(ruta):
            os.remove(ruta)

@app.route("/")
def index():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM contactos ORDER BY nombre")
    contactos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("index.html", contactos=contactos)

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        instagram = request.form.get("instagram", "").strip()

        if not nombre or not telefono or not categoria:
            flash("Completa los campos obligatorios")
            return redirect(url_for("agregar"))

        foto = guardar_foto(request.files.get("foto"))
        if foto is False:
            flash("Formato de foto no permitido")
            return redirect(url_for("agregar"))

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO contactos (nombre, telefono, correo, categoria, instagram, foto) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, telefono, correo, categoria, instagram, foto)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        flash("Contacto agregado")
        return redirect(url_for("index"))
    return render_template("agregar.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM contactos WHERE id = %s", (id,))
    contacto = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not contacto:
        flash("Contacto no encontrado")
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        instagram = request.form.get("instagram", "").strip()
        foto_anterior = contacto["foto"]

        if not nombre or not telefono or not categoria:
            flash("Completa los campos obligatorios")
            return redirect(url_for("editar", id=id))

        foto_nueva = guardar_foto(request.files.get("foto"))
        if foto_nueva is False:
            flash("Formato de foto no permitido")
            return redirect(url_for("editar", id=id))

        foto_final = foto_nueva if foto_nueva else foto_anterior

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE contactos SET nombre=%s, telefono=%s, correo=%s, categoria=%s, instagram=%s, foto=%s WHERE id=%s",
            (nombre, telefono, correo, categoria, instagram, foto_final, id)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        if foto_nueva:
            borrar_foto(foto_anterior)

        flash("Contacto actualizado")
        return redirect(url_for("index"))

    return render_template("editar.html", contacto=contacto)

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM contactos WHERE id = %s", (id,))
    contacto = cursor.fetchone()
    if contacto:
        borrar_foto(contacto["foto"])
        cursor.execute("DELETE FROM contactos WHERE id = %s", (id,))
        conexion.commit()
    cursor.close()
    conexion.close()
    flash("Contacto eliminado")
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

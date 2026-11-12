from flask import Flask, render_template, request, redirect, url_for, flash
from database import obtener_conexion, crear_tabla
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = "agenda_contactos_clave"

app.config["UPLOAD_FOLDER"] = os.path.join(
    "static", "uploads"
)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}

crear_tabla()


def guardar_foto(archivo):
    if not archivo or archivo.filename == "":
        return None

    nombre_original = secure_filename(archivo.filename)
    extension = nombre_original.rsplit(".", 1)[-1].lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        return False

    nombre_nuevo = str(uuid.uuid4()) + "." + extension
    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_nuevo)

    archivo.save(ruta)

    return nombre_nuevo


def borrar_foto(nombre):
    if nombre:
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)
        if os.path.isfile(ruta):
            os.remove(ruta)


@app.route("/")
def inicio():
    conexion = obtener_conexion()

    contactos = conexion.execute(
        "SELECT * FROM contactos ORDER BY nombre"
    ).fetchall()

    conexion.close()

    return render_template("index.html", contactos=contactos)


@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip()
    categoria = request.form.get("categoria", "").strip()
    instagram = request.form.get("instagram", "").strip()

    if not nombre or not telefono or not categoria:
        flash("Completa los campos obligatorios.")
        return redirect(url_for("inicio"))

    foto = guardar_foto(request.files.get("foto"))

    if foto is False:
        flash("Formato de foto no permitido.")
        return redirect(url_for("inicio"))

    conexion = obtener_conexion()

    conexion.execute("""
        INSERT INTO contactos
        (nombre, telefono, correo, categoria, instagram, foto)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, telefono, correo, categoria, instagram, foto))

    conexion.commit()
    conexion.close()

    flash("¡Contacto agregado correctamente!")
    return redirect(url_for("inicio"))


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = obtener_conexion()

    contacto = conexion.execute(
        "SELECT * FROM contactos WHERE id = ?", (id,)
    ).fetchone()

    if contacto is None:
        conexion.close()
        flash("El contacto no existe.")
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        instagram = request.form.get("instagram", "").strip()

        if not nombre or not telefono or not categoria:
            conexion.close()
            flash("Completa los campos obligatorios.")
            return redirect(url_for("editar", id=id))

        foto_anterior = contacto["foto"]
        foto_nueva = guardar_foto(request.files.get("foto"))

        if foto_nueva is False:
            conexion.close()
            flash("Formato de foto no permitido.")
            return redirect(url_for("editar", id=id))

        foto_final = foto_nueva if foto_nueva else foto_anterior

        conexion.execute("""
            UPDATE contactos
            SET nombre = ?, telefono = ?, correo = ?,
                categoria = ?, instagram = ?, foto = ?
            WHERE id = ?
        """, (
            nombre, telefono, correo, categoria,
            instagram, foto_final, id
        ))

        conexion.commit()
        conexion.close()

        if foto_nueva:
            borrar_foto(foto_anterior)

        flash("¡Contacto actualizado correctamente!")
        return redirect(url_for("inicio"))

    conexion.close()
    return render_template("editar.html", contacto=contacto)


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conexion = obtener_conexion()

    contacto = conexion.execute(
        "SELECT foto FROM contactos WHERE id = ?", (id,)
    ).fetchone()

    if contacto:
        borrar_foto(contacto["foto"])

        conexion.execute(
            "DELETE FROM contactos WHERE id = ?", (id,)
        )

        conexion.commit()

    conexion.close()

    flash("Contacto eliminado.")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)
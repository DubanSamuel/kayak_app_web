from flask import Flask, render_template, request, redirect, url_for
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os

app = Flask(__name__)

ARCHIVO = "registros_kayak.xlsx"


# ---------------- CREAR EXCEL ----------------
def crear_excel():
    if not os.path.exists(ARCHIVO):
        wb = Workbook()
        ws = wb.active
        ws.append(["Fecha", "Hora", "Tipo", "Valor"])
        wb.save(ARCHIVO)


# ---------------- LEER REGISTROS ----------------
def leer_registros():
    wb = load_workbook(ARCHIVO)
    ws = wb.active
    registros = []

    for fila in ws.iter_rows(min_row=2, values_only=True):
        registros.append({
            "fecha": fila[0],
            "hora": fila[1],
            "tipo": fila[2],
            "valor": fila[3]
        })

    return registros


# ---------------- GUARDAR TODO ----------------
def guardar_todo(registros):
    wb = Workbook()
    ws = wb.active
    ws.append(["Fecha", "Hora", "Tipo", "Valor"])

    for r in registros:
        ws.append([r["fecha"], r["hora"], r["tipo"], r["valor"]])

    wb.save(ARCHIVO)


# ---------------- INICIO ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    crear_excel()
    registros = leer_registros()

    fecha_buscar = request.form.get("fecha_buscar", "")

    if fecha_buscar:
        registros = [r for r in registros if r["fecha"] == fecha_buscar]

    total = sum(r["valor"] for r in registros if isinstance(r["valor"], int))

    return render_template(
        "index.html",
        registros=registros,
        total=total,
        fecha_buscar=fecha_buscar
    )


# ---------------- AGREGAR ----------------
@app.route("/agregar", methods=["POST"])
def agregar():
    tipo = request.form.get("tipo")

    valor = request.form.get("valor")
    valor = int(valor) if valor and valor.isdigit() else 0

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    wb = load_workbook(ARCHIVO)
    ws = wb.active
    ws.append([fecha, hora, tipo, valor])
    wb.save(ARCHIVO)

    return redirect(url_for("index"))


# ---------------- ELIMINAR ----------------
@app.route("/eliminar/<int:index>")
def eliminar(index):
    registros = leer_registros()
    if 0 <= index < len(registros):
        registros.pop(index)
        guardar_todo(registros)
    return redirect(url_for("index"))


# ---------------- EDITAR ----------------
@app.route("/editar/<int:index>", methods=["GET", "POST"])
def editar(index):
    registros = leer_registros()
    registro = registros[index]

    if request.method == "POST":
        registro["fecha"] = request.form["fecha"]
        registro["hora"] = request.form["hora"]
        registro["tipo"] = request.form["tipo"]

        valor = request.form["valor"]
        registro["valor"] = int(valor) if valor.isdigit() else 0

        guardar_todo(registros)
        return redirect(url_for("index"))

    return render_template("editar.html", r=registro, index=index)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

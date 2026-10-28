"""
Servidor Flask: muestra la interfaz web y reenvía al Arduino la clase
detectada por el modelo de Teachable Machine.

Uso:
    pip install -r requirements.txt
    python app.py
    Abrir http://127.0.0.1:5000 en Chrome
"""
import threading
import time

import serial
import serial.tools.list_ports
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

arduino = None
candado = threading.Lock()
ultima_letra = None


def letra_de_indice(indice: int) -> str:
    """Clase 0 -> 'A', clase 1 -> 'B', clase 2 -> 'C', etc."""
    return chr(ord("A") + indice)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/puertos")
def puertos():
    lista = [
        {"puerto": p.device, "descripcion": p.description}
        for p in serial.tools.list_ports.comports()
    ]
    return jsonify(lista)


@app.route("/api/conectar", methods=["POST"])
def conectar():
    global arduino, ultima_letra
    puerto = (request.get_json(silent=True) or {}).get("puerto")
    if not puerto:
        return jsonify(ok=False, error="Elige un puerto."), 400
    with candado:
        try:
            if arduino and arduino.is_open:
                arduino.close()
            arduino = serial.Serial(puerto, 9600, timeout=1)
            time.sleep(2)  # el Arduino Uno se reinicia al abrir el puerto
            ultima_letra = None
        except serial.SerialException as e:
            arduino = None
            return jsonify(ok=False, error=f"No se pudo abrir {puerto}: {e}"), 500
    return jsonify(ok=True)


@app.route("/api/desconectar", methods=["POST"])
def desconectar():
    global arduino
    with candado:
        if arduino and arduino.is_open:
            arduino.close()
        arduino = None
    return jsonify(ok=True)


@app.route("/api/clase", methods=["POST"])
def recibir_clase():
    """Recibe {"indice": 0, "nombre": "Mano abierta"} y manda la letra al Arduino."""
    global ultima_letra
    datos = request.get_json(silent=True) or {}
    indice = datos.get("indice")
    if not isinstance(indice, int) or indice < 0 or indice > 25:
        return jsonify(ok=False, error="Índice de clase inválido."), 400

    letra = letra_de_indice(indice)
    with candado:
        if not (arduino and arduino.is_open):
            return jsonify(ok=False, error="Arduino no conectado."), 409
        if letra != ultima_letra:  # solo enviar cuando cambia
            try:
                arduino.write(letra.encode())
                ultima_letra = letra
            except serial.SerialException as e:
                return jsonify(ok=False, error=str(e)), 500
    return jsonify(ok=True, letra=letra)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

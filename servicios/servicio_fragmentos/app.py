from flask import Flask, request, jsonify

app = Flask(__name__)

# Diccionario que almacena qué fragmentos tiene cada nodo
nodos_fragmentos = {}

@app.route("/nodos", methods=["GET"])
def listar_nodos():
    return jsonify(nodos_fragmentos)

@app.route("/nodos/<nombre>", methods=["GET"])
def obtener_fragmentos(nombre):
    if nombre not in nodos_fragmentos:
        return jsonify({"error": "Nodo no encontrado"}), 404
    return jsonify({nombre: nodos_fragmentos[nombre]})

@app.route("/nodos", methods=["POST"])
def registrar_nodo():
    data = request.get_json()
    nombre = data.get("nombre")
    fragmentos = data.get("fragmentos", [])

    if not nombre:
        return jsonify({"error": "Falta el nombre del nodo"}), 400

    nodos_fragmentos[nombre] = fragmentos
    return jsonify({nombre: fragmentos}), 201

@app.route("/nodos/<nombre>", methods=["PUT"])
def actualizar_fragmentos(nombre):
    if nombre not in nodos_fragmentos:
        return jsonify({"error": "Nodo no registrado"}), 404

    data = request.get_json()
    nuevos_fragmentos = data.get("fragmentos", [])
    nodos_fragmentos[nombre] = nuevos_fragmentos
    return jsonify({nombre: nuevos_fragmentos})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

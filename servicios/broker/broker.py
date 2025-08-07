from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# diccionario para guardar fragmentos por nodo
fragmentos_por_nodo = {}
nodos_registrados = {}


@app.route("/nodos/<nombre_nodo>/fragmentos", methods=['POST'])
def registrar_nodo(nombre_nodo):
    """
    Registra un nodo y los fragmentos que posee.
    ---
    tags:
      - Registro de Nodos
    parameters:
      - name: nombre_nodo
        in: path
        type: string
        required: true
        description: Nombre del nodo que se registra (ej. 'nodo1:6001')
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            fragmentos:
              type: array
              items:
                type: string
              description: Lista de nombres de los fragmentos que el nodo posee
    responses:
      200:
        description: Nodo y fragmentos registrados exitosamente
    """
    data = request.json
    fragmentos = data.get("fragmentos", [])

    # elimina registros viejos del nodo
    for f in list(fragmentos_por_nodo.keys()):
        if nombre_nodo in fragmentos_por_nodo[f]:
            fragmentos_por_nodo[f].remove(nombre_nodo)
            if not fragmentos_por_nodo[f]:
                del fragmentos_por_nodo[f]

    # registra nuevos fragmentos
    for fragmento in fragmentos:
        if fragmento not in fragmentos_por_nodo:
            fragmentos_por_nodo[fragmento] = []
        if nombre_nodo not in fragmentos_por_nodo[fragmento]:
            fragmentos_por_nodo[fragmento].append(nombre_nodo)

    nodos_registrados[nombre_nodo] = True
    print(f"Nodo '{nombre_nodo}' registrado. Tiene {len(fragmentos)} fragmentos.")
    return jsonify({"mensaje": "Nodo registrado"}), 200


@app.route("/fragmentos/<nombre_fragmento>/nodos", methods=['GET'])
def buscar_nodos_con_fragmento(nombre_fragmento):
    """
    Obtiene la lista de nodos que tienen un fragmento específico.
    ---
    tags:
      - Búsqueda de Fragmentos
    parameters:
      - name: nombre_fragmento
        in: path
        type: string
        required: true
        description: Nombre del fragmento a buscar
    responses:
      200:
        description: Lista de nodos que poseen el fragmento
        schema:
          type: object
          properties:
            nodos:
              type: array
              items:
                type: string
    """
    nodos = fragmentos_por_nodo.get(nombre_fragmento, [])
    return jsonify({"nodos": nodos}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
from flask import Flask, send_from_directory, jsonify
from flasgger import Swagger
import os
import requests
import sys
import time

app = Flask(__name__)
swagger = Swagger(app)

PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
# lee el nombre del servicio de docker
IP = os.environ.get('NODE_NAME', 'localhost')
NOMBRE_NODO = f"{IP}:{PUERTO}"

# detecta la carpeta de fragmentos
ruta_docker = f"/fragmentos_{PUERTO}"
ruta_local = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../fragmentos_{PUERTO}"))
CARPETA_FRAGMENTOS = ruta_docker if os.path.exists(ruta_docker) else ruta_local

# url base del broker
broker_URL = "http://broker:5000"

#registra el nodo en el broker con los fragmentos que tiene
def registrar_en_broker():
    try:
        if not os.path.exists(CARPETA_FRAGMENTOS):
            print(f"Error la carpeta de fragmentos '{CARPETA_FRAGMENTOS}' no existe.")
            return False

        fragmentos = os.listdir(CARPETA_FRAGMENTOS)
        url = f"{broker_URL}/nodos/{NOMBRE_NODO}/fragmentos"
        
        intentos_max = 10
        for i in range(intentos_max):
            try:
                r = requests.post(url, json={"fragmentos": fragmentos})
                if r.status_code == 200:
                    print(f"Nodo '{NOMBRE_NODO}' registrado con {len(fragmentos)} fragmentos.")
                    return True
                else:
                    print(f"Error al registrar nodo: {r.text}")
                    return False
            except requests.exceptions.ConnectionError:
                print(f"Intentando conectar con el broker... (Intento {i+1}/{intentos_max})")
                time.sleep(2)
        
        print("No se pudo conectar con el broker después de varios intentos.")
        return False
    except FileNotFoundError:
        print(f"Error: La carpeta de fragmentos '{CARPETA_FRAGMENTOS}' no existe.")
        return False

#Consulta al broker para obtener una lista de nodos que tienen un fragmento
def buscar_nodos_con_fragmento(nombre_fragmento):
    try:
        url = f"{broker_URL}/fragmentos/{nombre_fragmento}/nodos"
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return datos.get("nodos", [])
        else:
            print(f"No se pudo consultar el broker: {respuesta.text}")
    except Exception as e:
        print(f"Error consultando broker: {e}")
    return []

#Descarga un fragmento desde otro nodo que lo tenga
def descargar_fragmento_de_nodo(nodo, nombre_fragmento):
    try:
        host, port_str = nodo.split(":")
        url = f"http://{host}:{port_str}/fragmentos/{nombre_fragmento}"
        
        # usa streaming para archivos grandes
        respuesta = requests.get(url, stream=True)
        
        if respuesta.status_code == 200:
            ruta_guardado = os.path.join(CARPETA_FRAGMENTOS, nombre_fragmento)
            with open(ruta_guardado, 'wb') as f:
                for chunk in respuesta.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Fragmento '{nombre_fragmento}' descargado desde '{nodo}'.")
            
            # logica p2p, se vuelve a registrar
            registrar_en_broker()
            return True
        else:
            print(f"Fragmento no encontrado en nodo '{nodo}'")
    except Exception as e:
        print(f"Error descargando fragmento de '{nodo}': {e}")
    return False


@app.route('/descargar/<nombre_fragmento>', methods=['GET'])
def descargar_fragmento(nombre_fragmento):
    """
    Endpoint para solicitar la descarga de un fragmento.
    ---
    tags:
      - Cliente
    parameters:
      - name: nombre_fragmento
        in: path
        type: string
        required: true
        description: Nombre del fragmento a descargar
    responses:
      200:
        description: Fragmento descargado exitosamente.
      404:
        description: Fragmento no encontrado en ningún nodo.
      500:
        description: Error al descargar el fragmento.
    """
    nodos = buscar_nodos_con_fragmento(nombre_fragmento)
    if not nodos:
        return jsonify({"error": "El fragmento no se encontro en ningun nodo"}), 404

    # busca y descarga del primer nodo disponible
    for nodo in nodos:
        if nodo != NOMBRE_NODO:
            if descargar_fragmento_de_nodo(nodo, nombre_fragmento):
                return jsonify({"mensaje": f"Fragmento '{nombre_fragmento}' descargado de '{nodo}'."}), 200
    
    # si no se pudo descargar en ningun nodo
    return jsonify({"error": "No fue posible descargar el fragmento desde los nodos disponibles"}), 500


@app.route("/fragmentos/<nombre>", methods=['GET'])
def enviar_fragmento(nombre):
    """
    Endpoint para que otros nodos descarguen un fragmento.
    ---
    tags:
      - Intercambio P2P
    parameters:
      - name: nombre
        in: path
        type: string
        required: true
        description: Nombre del fragmento a enviar
    responses:
      200:
        description: Archivo fragmento encontrado y enviado
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      404:
        description: Fragmento no encontrado
    """
    ruta_fragmento = os.path.join(CARPETA_FRAGMENTOS, nombre)
    if os.path.exists(ruta_fragmento):
        return send_from_directory(CARPETA_FRAGMENTOS, nombre)
    else:
        return jsonify({"error": "Fragmento no encontrado"}), 404


@app.route("/mis_fragmentos", methods=['GET'])
def listar_fragmentos():
    """
    Lista todos los fragmentos disponibles localmente en este nodo.
    ---
    tags:
      - Cliente
    responses:
      200:
        description: Lista de fragmentos encontrados
        schema:
          type: object
          properties:
            fragmentos:
              type: array
              items:
                type: string
    """
    fragmentos_existentes = os.listdir(CARPETA_FRAGMENTOS) if os.path.exists(CARPETA_FRAGMENTOS) else []
    return jsonify({"fragmentos": fragmentos_existentes})

@app.route("/nodos/<nombre_nodo>/fragmentos", methods=['GET'])
def obtener_fragmentos_de_nodo(nombre_nodo):
    """
    Obtiene la lista de fragmentos que posee un nodo específico consultando al broker.
    ---
    tags:
      - Cliente
    parameters:
      - name: nombre_nodo
        in: path
        type: string
        required: true
        description: Nombre del nodo a consultar (ej. 'nodo1:6001')
    responses:
      200:
        description: Lista de fragmentos que tiene el nodo
        schema:
          type: object
          properties:
            fragmentos:
              type: array
              items:
                type: string
      404:
        description: Nodo no encontrado en el broker.
    """
    try:
        url = f"{broker_URL}/nodos/{nombre_nodo}/fragmentos"
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return jsonify(datos), 200
        else:
            return jsonify({"error": "Nodo no encontrado en el broker"}), 404
    except Exception as e:
        print(f"Error al consultar el broker: {e}")
        return jsonify({"error": "Error interno al consultar el broker"}), 500

if __name__ == "__main__":
    if not os.path.exists(CARPETA_FRAGMENTOS):
        os.makedirs(CARPETA_FRAGMENTOS)
        print(f"INFO: Carpeta de fragmentos creada en '{CARPETA_FRAGMENTOS}'")

    # espera a que el broker se inicie
    time.sleep(5) 
    registrar_en_broker()
    
    app.run(host="0.0.0.0", port=PUERTO)

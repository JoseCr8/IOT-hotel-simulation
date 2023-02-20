from flask import Flask, request
from flask_cors import CORS
import os, requests, json

app = Flask(__name__)
CORS(app)


# Se encarga de mandar el comando hacia el router_msg para que este lo mande al twin
def insert_device_state(params):
    r = requests.post(
        ROUTER_MSG_API_URL+"/device_state",
        json=params
    )
    return r


# Recupera la inforamacion de lo sensores de la base de datos a traves del data_ingestion_microservice
def get_device_state():
    r = requests.get(DATA_INGESTION_API_URL+"/device_state")
    print("enviado sensor", r)
    return json.dumps(r.json())


def get_room_state():
    r = requests.get(DATA_INGESTION_API_URL+"/room_list")
    print("enviado habitacion", r)
    return json.dumps(r.json())


# Se encarga de manejar las peticiones del frontend para mandar comandos o para solicitar la info de los sensores
@app.route('/device_state', methods=['GET', 'POST'])
def device_state():
    if request.method == 'POST':
        params = request.get_json()
        if len(params) != 3:
            return {"response": "Incorrect parameters"}
        mycursor = insert_device_state(params)
        print("response: ", mycursor)
        return json.dumps(mycursor.json())
    elif request.method == 'GET':
        return get_device_state()


@app.route('/room_state', methods=['GET', 'POST'])
def room_state():
    if request.method == 'POST':
        params = request.get_json()
        # mycursor = insert_device_state(params)
        print("response: no deberias de usar esto")
        return "si"  # json.dumps(mycursor.json())
    elif request.method == 'GET':
        return get_room_state()



DATA_INGESTION_API_URL = "http://" + os.getenv("DATA_INGESTION_API_ADDRESS") + ":" + os.getenv("DATA_INGESTION_API_PORT")
ROUTER_MSG_API_URL = "http://" + os.getenv("ROUTER_MSG_API_ADDRESS") + ":" + os.getenv("ROUTER_MSG_API_PORT")
HOST = os.getenv('HOST_B')
PORT = os.getenv('PORT_B')
app.run(host=HOST, port=PORT, debug=True)
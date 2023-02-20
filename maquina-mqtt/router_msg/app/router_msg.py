import time, os, requests, json
import paho.mqtt.client as mqtt
from flask import Flask, request
from flask_cors import CORS

MQTT_SERVER_1 = os.getenv("MQTT_SERVER_ADDRESS_1")
MQTT_PORT_1 = int(os.getenv("MQTT_SERVER_PORT_1"))
MQTT_SERVER_TELEMETRY = os.getenv("MQTT_SERVER_ADDRESS_2")
MQTT_PORT_TELEMETRY = int(os.getenv("MQTT_SERVER_PORT_2"))
# Para data_ingestion
API_URL = "http://" + os.getenv("API_SERVER_ADDRESS") + ":" + os.getenv("API_SERVER_PORT")
# Para el backend
API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))
index_room = 1
saved_rooms = {}

app = Flask(__name__)


# Metodo para mandar comandos a la raspy a traves de la publicacion de estos para su lectura por el twin
def send_command(params):
    type_dev = params["type"]
    value = params["value"]
    room = params["room"]
    topic = "hotel/rooms/"+room+"/command"
    if type_dev == "air-conditioner-mode":
        client.publish(topic + "/air_conditioner", payload=json.dumps({"mode": value}), qos=0, retain=True)
        print("Command message sent through " + topic + "/air_conditioner")
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    if type_dev == "outside-light-mode":
        client.publish(topic + "/outside_light", payload=json.dumps({"active": value}), qos=0, retain=True)
        print("Command message sent through " + topic)
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    if type_dev == "outside-light-value":
        client.publish(topic + "/outside_light_value", payload=json.dumps({"value": value}), qos=0, retain=True)
        print("Command message sent through " + topic)
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    if type_dev == "indoor-light-mode":
        client.publish(topic + "/indoor_light", payload=json.dumps({"active": value}), qos=0, retain=True)
        print("Command message sent through " + topic)
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    if type_dev == "indoor-light-value":
        client.publish(topic + "/indoor_light_value", payload=json.dumps({"value": value}), qos=0, retain=True)
        print("Command message sent through " + topic)
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    if type_dev == "blinds-mode":
        client.publish(topic + "/blind", payload=json.dumps({"mode": value}), qos=0, retain=True)
        print("Command message sent through " + topic)
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    if type_dev == "blinds-value":
        client.publish(topic + "/blind_value", payload=json.dumps({"value": value}), qos=0, retain=True)
        print("Command message sent through " + topic)
        requests.post(
            API_URL + "/commands",
            json={"room": room, "command": type_dev, "value": value}
        )
        return {"response": "Message successfully sent"}

    else:
        return {"response": "Incorrect type param"}


# Se hace cargo de las peticones de envio de commandos
@app.route('/device_state', methods=['POST'])
def device_state():
    if request.method == 'POST':
        params = request.get_json()
        return send_command(params)


# Metodo encargado de las subscripciones a los topicos cuando se establezca conexion con el mqtt
def on_connect(client, userdata, flags, rc):
    print("Connected on subscriber with code", rc)
    client.subscribe("hotel/rooms/+/telemetry/+")
    print("Subscribed to all telemetry")
    client.subscribe("hotel/rooms/+/config")
    print("Subscribed to all rooms config")
    client.subscribe("hotel/rooms/+/connection")
    print("Subscribed to all rooms last_will")


# Metodo encargado de la respuesta a dar cuando se publica un mensaje en alguno de los topico subscritos
def on_message(client, userdata, msg):
    global index_room, saved_rooms
    print("Mensaje recibido en ", msg.topic, "con mensaje", msg.payload.decode())
    topic = (msg.topic).split('/')

    # Si el mensaje se ha publicado en el topico de configuracion
    if topic[-1] == "config":
        # Solicitamos las habitaciones registradas
        r = requests.get(API_URL + "/room_list")
        saved_rooms = r.json()
        # print("SAVED_ROOMS", saved_rooms)
        room_id = msg.payload.decode()
        found = False
        num_hab = []
        nums = []
        decenas = False
        # Si la base de datos esta vacía
        if saved_rooms == []:
            index_room = 1
            room_name = "Room" + str(index_room)
            found = True
        else:
            # Se busca itera por la lista de diccionarios con la informacion de las habitaciones
            for i in saved_rooms:
                num_hab.append(i['room'])
                # Si la habitacion ya esta registrada se guarda en la variable global la informacion de la base de datos
                if i['room_id'] == room_id:
                    room_name = i['room']
                    found = True
            num_hab.sort()
            # print(num_hab)
            # Se guardan los numeros de habitacion en una lista por si hiciera falta asignar uno nuevo
            for a in num_hab:
                if len(a) > 5:
                    nums.append(int(a[-2:]))
                    decenas = True
                else :
                    nums.append(int(a[-1]))
        # Si no se ha encontrado en la lista dada por la base de datos se asgina el numero más alto registrado + 1
        if found == False:
            nums.sort()
            index_room = nums[-1] + 1
            room_name = "Room" + str(index_room)
        print("Digital with id", msg.payload.decode(), "saved as", room_name)
        # Almacenamos la habitacion en la base de datos
        requests.post(
                API_URL + "/room_list",
                json={"room_num": room_name, "room_id": room_id, "type": "connection", "connection_status": "online", "last_connection": ""}
        )
        # Publicamos el numero de habitacion para el twin
        client.publish(msg.topic + "/room", payload=room_name, qos=0, retain=True)
        print("Publicado", room_name, "en TOPIC", msg.topic)

    # Si el mensaje se ha publicado en alguno de los topicos de telemetria
    if "telemetry" in topic:
        # Sacamos el numero de habitacion del topic
        room_name = topic[2]
        # Lecturas de sensores
        payload = json.loads(msg.payload)
        value = -1
        print(payload)
        if topic[-1] == "temperature":
            value = payload["temperature"]["temperature"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
        if topic[-1] == "air_conditioner":
            value = payload["air_conditioner"]["level"]
            print("VALUE",value)
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": "air_level", "value": value}
            )
            mode = payload["air_conditioner"]["mode"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": "air_mode", "value": mode}
            )
        if topic[-1] == "presence":
            value = payload["presence"]["detected"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
        if topic[-1] == "blind":
            value = payload["blind"]["active"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
            value = payload["blind"]["level"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": "blinds_mode", "value": value}
            )
        if topic[-1] == "indoor_light":
            value = payload["indoor_light"]["level"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
            value = payload["indoor_light"]["active"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": "indoor_mode", "value": value}
            )
        if topic[-1] == "outside_light":
            value = payload["outside_light"]["level"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
            value = payload["outside_light"]["active"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": "outside_mode", "value": value}
            )
    if "connection" in topic:
        print("recibido: ", msg.payload.decode(), "desde", topic[-2])
        room_id = topic[-2]
        room_name = ""
        r = requests.get(API_URL + "/room_list")
        saved_rooms = r.json()
        for i in saved_rooms:
            # Si la habitacion ya esta registrada se guarda en la variable global la informacion de la base de datos
            if i['room_id'] == room_id:
                room_name = i['room']
        requests.post(
            API_URL + "/room_list",
            json={"room_num": room_name, "room_id": room_id, "type": "connection", "connection_status": msg.payload.decode(), "last_connection": ""}
        )
client = mqtt.Client()
client.username_pw_set(username="dso_user", password="dso_password")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER_1, MQTT_PORT_1, 60)
client.loop_start()
CORS(app)
app.run(host=API_HOST, port=API_PORT, debug=False)

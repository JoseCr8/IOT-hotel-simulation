import time, os, random, subprocess, json
import paho.mqtt.client as mqtt


def get_host_name():
    bashCommandName = 'echo $HOSTNAME'
    host = subprocess \
               .check_output(['bash', '-c', bashCommandName]) \
               .decode("utf-8")[0:-1]
    return host


# IP GCP con las mqtt
MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
# Puerto mqtt twin-router_msg
MQTT_PORT = int(os.getenv("MQTT_SERVER_PORT_1"))
# Puerto mqtt twin-raspy
MQTT_PORT_RASPY = int(os.getenv("MQTT_SERVER_PORT_2"))
ROOM_ID = get_host_name()
CONFIG_TOPIC = "hotel/rooms/" + ROOM_ID + "/config"
# Variables
room_number = ""
sensors = {}
air_conditioner_mode = ""
blinds_angle = 0
blinds_mode = ""
indoor_state = ""
indoor_level = 0
outside_state = ""
outside_level = 0
conectado_raspy = ""
command_receiver = ""
# historial
air_conditioner_mode_old = ""
blinds_angle_old = 0
blinds_mode_old = ""
indoor_state_old = ""
indoor_level_old = 0
outside_state_old = ""
outside_level_old = 0
command = False

def randomize_sensors():
    global sensors
    sensors = {
        "indoor_light": {
            "active": random.randint(0, 1),
            "level": random.randint(0, 100)
        },
        "outside_light": {
            "active": random.randint(0, 1),
            "level": random.randint(0, 100)
        },
        "blind": {
            "active": random.randint(0, 1),
            "level": random.randint(0, 100)
        },
        "air_conditioner": {
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(10, 30),
            "mode": random.randint(0, 2)
        },
        "presence": {
            "active": True if random.randint(0, 1) == 1 else False,
            "detected": True if random.randint(0, 1) == 1 else False
        },
        "temperature": {  # room temperature
            "active": True if random.randint(0, 1) == 1 else False,
            "temperature": random.randint(0, 40)
        }
    }


def on_connect(client, userdata, flags, rc):
    print("Twin conectado con codigo: ", rc)
    client.subscribe(CONFIG_TOPIC + "/room")
    print("suscrito a ", CONFIG_TOPIC + "/room")
    client.publish(CONFIG_TOPIC, payload=ROOM_ID, qos=0, retain=False)
    print("Enviado el id", ROOM_ID, "con topic", CONFIG_TOPIC)


def on_message(client, userdata, msg):
    global room_number, air_conditioner_mode, blinds_angle, indoor_state, indoor_level, outside_state, outside_level, blinds_mode
    global air_conditioner_mode_old, blinds_angle_old, indoor_state_old, outside_state_old, blinds_mode_old, indoor_level_old, outside_level_old
    global command, command_receiver
    room_number_a = msg.payload.decode()
    topic = (msg.topic).split('/')
    if "config" in topic:
        if topic[-1] == "room":
            room_number = room_number_a
            print("Numero de habtacion recivido como: ", room_number)

    if "command" in topic:
        payload = json.loads(msg.payload)
        if topic[-1] == "air_conditioner":
            air_conditioner_mode_old = air_conditioner_mode
            air_conditioner_mode = payload["mode"]
            print("recived command for ", topic[-1], " with mode ", air_conditioner_mode)
            command_receiver = "air_conditioner"
            command = True
            # return air_conditioner_mode
        if topic[-1] == "blind":
            blinds_mode_old = blinds_mode
            blinds_mode = payload["mode"]
            print("recived command for ", topic[-1], " with angle ", blinds_mode)
            command_receiver = "blind"
            command = True
            # return blinds_angle
        if topic[-1] == "blind_value":
            blinds_angle_old = blinds_angle
            blinds_angle = payload["value"]
            print("recived command for ", topic[-1], " with angle ", blinds_angle)
            command_receiver = "blind_value"
            command = True

        if topic[-1] == "indoor_light":
            indoor_state_old = indoor_state
            indoor_state = payload["active"]
            print("recived command for ", topic[-1], " with state", indoor_state)  # " and level ", indoor_level
            command_receiver = "indoor_light"
            command = True
        # return indoor_state
        if topic[-1] == "indoor_light_value":
            indoor_level_old = indoor_level
            indoor_level = payload["value"]
            print("recived command for ", topic[-1], " with state", indoor_level)  # " and level ", indoor_level
            command_receiver = "indoor_light_value"
            command = True

        if topic[-1] == "outside_light":
            outside_state_old = outside_state
            outside_state = payload["active"]
            print("recived command for ", topic[-1], " with state", outside_state)  # " and level ", indoor_level
            command_receiver = "outside_light"
            command = True
            # return outside_state

        if topic[-1] == "outside_light_value":
            outside_level_old = outside_level
            outside_level = payload["value"]
            print("recived command for ", topic[-1], " with state", outside_level)  # " and level ", indoor_level
            command_receiver = "outside_light_value"
            command = True


def on_connect_raspy(client, userdata, flags, rc):
    print("Twin conectado con codigo: ", rc)
    client.subscribe("hotel/rooms/" + room_number + "/raspy/+")
    print("suscrito a ", "hotel/rooms/" + room_number + "/raspy")


def on_message_raspy(client, userdata, msg):
    global conectado_raspy, sensors
    topic = (msg.topic).split('/')
    if "room" in topic:
        conectado_raspy = msg.payload.decode()
        if conectado_raspy == "connected":
            print("##Habitacion conctada", topic[-1], "mensaje", conectado_raspy)
        if conectado_raspy == "offline":
            print("##Habitacion desconectada", topic[-1], "mensaje", conectado_raspy)
    if "sensors" in topic:
        sensors = json.loads(msg.payload)
        print("##Mediciones habitacion", topic[-1],"sensores", sensors)

client = mqtt.Client()
client.username_pw_set(username="dso_user", password="dso_password")
client.on_connect = on_connect
client.on_message = on_message
client.will_set("hotel/rooms/" + ROOM_ID + "/connection", payload="offline", qos=0, retain=True)
client.connect(MQTT_SERVER, MQTT_PORT, 60)

client.loop_start()
while room_number == "":
    time.sleep(1)

client_2 = mqtt.Client()
client_2.username_pw_set(username="dso_user", password="dso_password")
client_2.on_connect = on_connect_raspy
client_2.on_message = on_message_raspy
#client_2.will_set("hotel/rooms/" + ROOM_ID + "/connection", payload="offline", qos=0, retain=True)
client_2.connect(MQTT_SERVER, MQTT_PORT_RASPY, 60)
client_2.loop_start()

COMMAND_TOPIC = "hotel/rooms/"+room_number+"/command/+"
client.subscribe(COMMAND_TOPIC)
print("suscrito a ", COMMAND_TOPIC)
TELEMETRY_TOPIC = "hotel/rooms/" + room_number + "/telemetry/"
TEMPERATURE_TOPIC = TELEMETRY_TOPIC + "temperature"
AIR_CONDITIONER_TOPIC = TELEMETRY_TOPIC + "air_conditioner"
BLIND_TOPIC = TELEMETRY_TOPIC + "blind"
PRESENCE_TOPIC = TELEMETRY_TOPIC + "presence"
INDOOR_LIGHT_TOPIC = TELEMETRY_TOPIC + "indoor_light"
OUTSIDE_LIGHT_TOPIC = TELEMETRY_TOPIC + "outside_light"

while True:
    if conectado_raspy == "" or conectado_raspy == "offline":
        randomize_sensors()
        print("modo simulacion\n")

    if command == True:
        if command_receiver == "air_conditioner":
            if air_conditioner_mode_old == air_conditioner_mode:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/air_conditioner",
                                 payload=json.dumps({"air_conditioner": air_conditioner_mode}), qos=0, retain=False)

        if command_receiver == "blind":
            if blinds_mode_old == blinds_mode:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/blind",
                                 payload=json.dumps({"blind": blinds_mode}), qos=0, retain=False)

        if command_receiver == "blind_value":
            if blinds_angle_old == blinds_angle:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/blind_value",
                                 payload=json.dumps({"blind_value": blinds_angle}), qos=0, retain=False)

        if command_receiver == "indoor_light":
            if indoor_state_old == indoor_state:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/indoor_light",
                                 payload=json.dumps({"indoor_light": indoor_state}), qos=0, retain=False)

        if command_receiver == "indoor_light_value":
            if indoor_level_old == indoor_level:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/indoor_light_value",
                                 payload=json.dumps({"indoor_light_value": indoor_level}), qos=0, retain=False)

        if command_receiver == "outside_light":
            if outside_state_old == outside_state:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/outside_light",
                                 payload=json.dumps({"outside_light": outside_state}), qos=0, retain=False)

        if command_receiver == "outside_light_value":
            if outside_level_old == outside_level:
                print("already_set")
            else:
                client_2.publish("hotel/rooms/" + room_number + "/raspy/command/outside_light_value",
                                 payload=json.dumps({"outside_light_value": outside_level}), qos=0, retain=False)

        command = False

    json_temperature = json.dumps({"temperature": {"active": sensors["temperature"]["active"],
                                                   "temperature": sensors["temperature"]["temperature"]}})

    json_air = json.dumps({"air_conditioner": {"active": sensors["air_conditioner"]["active"],
                                               "level": sensors["air_conditioner"]["level"],
                                               "mode": sensors["air_conditioner"]["mode"]}})

    json_blind = json.dumps({"blind": {"active": sensors["blind"]["active"],
                                       "level": sensors["blind"]["level"]}})

    json_presence = json.dumps({"presence": {"active": sensors["presence"]["active"],
                                             "detected": sensors["presence"]["detected"]}})

    json_indoor_light = json.dumps({"indoor_light": {"active": sensors["indoor_light"]["active"],
                                                     "level": sensors["indoor_light"]["level"]}})

    json_outside_light = json.dumps({"outside_light": {"active": sensors["outside_light"]["active"],
                                                       "level": sensors["outside_light"]["level"]}})
    # Temperatura
    client.publish(TEMPERATURE_TOPIC, payload=json_temperature, qos=0, retain=False)
    print(json_temperature)
    #print("Publicado", json_temperature, "en", TEMPERATURE_TOPIC)
    # Aire acondicionado
    client.publish(AIR_CONDITIONER_TOPIC, payload=json_air, qos=0, retain=False)
    print(json_air)
    #print("Publicado", json_air, "en", AIR_CONDITIONER_TOPIC)
    # Persiana
    client.publish(BLIND_TOPIC, payload=json_blind, qos=0, retain=False)
    print(json_blind)
    #print("Publicado", json_blind, "en", BLIND_TOPIC)
    # Presencia
    client.publish(PRESENCE_TOPIC, payload=json_presence, qos=0, retain=False)
    print(json_presence)
    # Luz interior
    client.publish(INDOOR_LIGHT_TOPIC, payload=json_indoor_light, qos=0, retain=False)
    print(json_indoor_light)
    # Luz exterior
    client.publish(OUTSIDE_LIGHT_TOPIC, payload=json_outside_light, qos=0, retain=False)
    print(json_outside_light)

    time.sleep(2)
    #time.sleep(random.randint(5, 20))

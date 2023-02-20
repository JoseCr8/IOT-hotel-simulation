import threading
from threading import Semaphore
import RPi.GPIO as GPIO
import time, os, random, subprocess, json
import Adafruit_DHT
import datetime
from datetime import date
import random
import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# pins
redPin = 16
greenPin = 20
bluePin = 16
motor1 = 23  # 18
motor2 = 24
enable = 26  # 25
button = 19
luz_int = 6
luz_ext = 5
servoPIN = 12

# variables globales
humedad = 0
pulsacion = 0
temperatura = 0
velocidad = 20
intesidad_interior = 0
corriente_interior = 0
intesidad_exterior = 0
corriente_exterior = 0
persiana_movimiento = 0
persiana_angulo = 0
ac_modo = 0
# set pins as outputs
GPIO.setup(enable, GPIO.OUT)
motor = GPIO.PWM(enable, 100)
motor.start(0)

GPIO.setup(luz_int, GPIO.OUT)
luz_interior = GPIO.PWM(luz_int, 100)
luz_interior.start(0)

GPIO.setup(luz_ext, GPIO.OUT)
luz_exterior = GPIO.PWM(luz_ext, 100)
luz_exterior.start(0)

GPIO.setup(motor1, GPIO.OUT)
GPIO.setup(motor2, GPIO.OUT)

GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50)
p.start(2.5)


GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)
GPIO.setup(bluePin, GPIO.OUT)

# MQTT
MQTT_SERVER = "34.79.175.189"
MQTT_PORT = 1884 #######
room_number = "Room1"
CONFIG_TOPIC = "hotel/rooms/" + room_number + "/raspy"
SENSORS_TOPIC = "hotel/rooms/" + room_number + "/raspy/sensors"
COMMAND_TOPIC = "hotel/rooms/" + room_number + "/raspy/command/+"


def on_connect(client, userdata, flags, rc):
    print("Twin conectado con codigo: ", rc)
    client.subscribe(CONFIG_TOPIC + "/room")
    print("suscrito a ", CONFIG_TOPIC + "/room")
    client.publish(CONFIG_TOPIC + "/room", payload="connected", qos=0, retain=False)

    client.subscribe(COMMAND_TOPIC)
    print("suscrito a ", COMMAND_TOPIC)


def on_message(client, userdata, msg):
    global room_number, temperatura, velocidad, pulsacion, intesidad_interior, corriente_interior, intesidad_exterior, corriente_exterior, persiana_movimiento, persiana_angulo, ac_modo
    topic = (msg.topic).split('/')
    if "command" in topic:
        payload = json.loads(msg.payload)
        if topic[-1] == "air_conditioner":
            ac_modo = int(payload["air_conditioner"])
            print("actualizado aire_ac a:", ac_modo)
        if topic[-1] == "blind":
            persiana_movimiento = int(payload["blind"])
            print("actualizado movimiento persiana a:", persiana_movimiento)
        if topic[-1] == "blind_value":
            persiana_angulo = int(payload["blind_value"])
            print("actializado persiana angulo a:", persiana_angulo)
        if topic[-1] == "indoor_light":
            corriente_interior = int(payload["indoor_light"])
            print("intensidad de luz interior actualizado a:", corriente_interior)
        if topic[-1] == "indoor_light_value":
            intesidad_interior = int(payload["indoor_light_value"])
            print("luz interior actualizada a:", intesidad_interior)
        if topic[-1] == "outside_light":
            corriente_exterior = int(payload["outside_light"])
            print("intensidad exterior actualizada a:", corriente_exterior)
        if topic[-1] == "outside_light_value":
            intesidad_exterior = int(payload["outside_light_value"])
            print("luz exterior actualizada a:", intesidad_exterior)


# Codigo sensores
def boton():
    global pulsacion
    pressed = False
    while True:
        if not GPIO.input(button):
            print("################# Boton Pulsado ################")
            pressed = True
            #return True
        if pressed == True:
            pulsacion += 1
            pressed = False
            print(pulsacion)
        time.sleep(0.5)


def weatherSensor():
    DHT_SENSOR = Adafruit_DHT.DHT11
    DHT_PIN = 10
    global pulsacion
    global temperatura
    global humedad

    while True:
        if pulsacion % 2 != 0:
            humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
            if humidity is not None and temperature is not None:
                temperatura = temperature
                humedad = humidity
                print("Humidity={0:0.1f}%".format(humidity))
                print("Temp={0:0.1f}C".format(temperature))
            else:
                print("Sensore failure")
        time.sleep(2)


def hilo_motor():
    global temperatura
    global humedad
    global pulsacion, velocidad, ac_modo
    while True:
        if pulsacion % 2 != 0:
            if ac_modo == 2:
                GPIO.output(motor1, GPIO.LOW)
                GPIO.output(motor2, GPIO.LOW)
            else:
                print("ac on")
                GPIO.output(motor1, GPIO.HIGH)
                GPIO.output(motor2, GPIO.LOW)
                motor.ChangeDutyCycle(100)
                velocidad = 100

        time.sleep(5)


def hilo_servomotor():
    global persiana_angulo, persiana_movimiento
    hold=0
    while True:
        if persiana_movimiento==0:
            if persiana_angulo<=89 and  hold==0:
                p.ChangeDutyCycle(2)
                time.sleep(0.5)
                p.ChangeDutyCycle(7.5)
                time.sleep(0.5)
                p.ChangeDutyCycle(12.5)
                time.sleep(0.5)
                hold=1
            if persiana_angulo >=90 and persiana_angulo<=180 and hold==1:
                p.ChangeDutyCycle(12.5)
                time.sleep(0.5)
                p.ChangeDutyCycle(7.5)
                time.sleep(0.5)
                p.ChangeDutyCycle(2)
                time.sleep(0.5)
                hold = 0

    return


def hilo_luz_inte():
    global intesidad_interior, corriente_interior
    # 0 off 1 on
    while True:
        if corriente_interior == 0:
            luz_interior.ChangeDutyCycle(0)
        else:
            if intesidad_interior > 100:
                print("valor demasiado alto")
            else:
                luz_interior.ChangeDutyCycle(intesidad_interior)
                print("intensidad interior: ", intesidad_interior)

        time.sleep(2)


def hilo_luz_ext():
    global intesidad_exterior, corriente_exterior
    # 0 off 1 on
    while True:
        if corriente_exterior == 0:
            luz_exterior.ChangeDutyCycle(0)
        else:
            if intesidad_exterior > 100:
                print("valor demasiado alto")
            else:
                luz_exterior.ChangeDutyCycle(intesidad_exterior)
                print("intensidad exterior: ", intesidad_exterior)

        time.sleep(2)


def hilo_led():
    global temperatura
    global pulsacion, ac_modo
    while True:
        if pulsacion % 2 != 0:
            if ac_modo == 2:
                # Apagado
                GPIO.output(redPin, GPIO.LOW)
                GPIO.output(greenPin, GPIO.LOW)
                GPIO.output(bluePin, GPIO.LOW)
            elif ac_modo == 0:  # Frio
                # Azul
                GPIO.output(redPin, GPIO.LOW)
                GPIO.output(greenPin, GPIO.HIGH)
                GPIO.output(bluePin, GPIO.LOW)
            elif ac_modo == 1:  # Calor
                # Rojo
                GPIO.output(redPin, GPIO.LOW)
                GPIO.output(greenPin, GPIO.LOW)
                GPIO.output(bluePin, GPIO.HIGH)
        time.sleep(2)



def hilo_estado():
    global temperatura, velocidad, pulsacion, intesidad_interior, corriente_interior, intesidad_exterior, corriente_exterior, persiana_movimiento, persiana_angulo, ac_modo
    sensors = {}
    while True:
        sensors = {
            "indoor_light": {
                "active": corriente_interior,
                "level": intesidad_interior
            },
            "outside_light": {
                "active": corriente_exterior,
                "level": intesidad_exterior
            },
            "blind": {
                "active": persiana_movimiento,
                "level": persiana_angulo
            },
            "air_conditioner": {
                "active": True if pulsacion % 2 != 0 else False,
                "level": velocidad,
                "mode": ac_modo
            },
            "presence": {
                "active": True if pulsacion % 2 != 0 else False,
                "detected": True if pulsacion % 2 != 0 else False
            },
            "temperature": {  # room temperature
                "active": True if pulsacion % 2 != 0 else False,
                "temperature": temperatura
            }
        }
        client.publish(SENSORS_TOPIC, payload=json.dumps(sensors), qos=0, retain=False)
        time.sleep(2)

client = mqtt.Client()
client.username_pw_set(username="dso_user", password="dso_password")
client.on_connect = on_connect
client.on_message = on_message
client.will_set(CONFIG_TOPIC + "/room", payload="offline", qos=0, retain=True)
client.connect(MQTT_SERVER, MQTT_PORT, 60)
client.loop_start()

try:
    botoncito = threading.Thread(target=boton)
    servo = threading.Thread(target=hilo_servomotor)
    humedades = threading.Thread(target=weatherSensor)
    luz_inter = threading.Thread(target=hilo_luz_inte)
    luz_exter = threading.Thread(target=hilo_luz_ext)
    luz = threading.Thread(target=hilo_led)
    #engine = threading.Thread(target=hilo_motor)
    estado = threading.Thread(target=hilo_estado, daemon=True)
    botoncito.start()
    #engine.start()
    servo.start()
    humedades.start()
    luz_inter.start()
    luz_exter.start()
    luz.start()
    estado.start()
    botoncito.join()
    #engine.join()
    servo.join()
    humedades.join()
    luz_inter.join()
    luz_exter.join()
    luz.join()
    estado.join()
except KeyboardInterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()

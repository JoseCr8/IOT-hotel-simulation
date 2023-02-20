import mysql.connector, json, os, sys
from datetime import datetime, date
from flask import Flask, request
from flask_cors import CORS


# Conexion con la base de datos en mariaDB
def connect_database():
    mydb = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return mydb


# Para guardar las lecturas de los sensores en la tabla device_state
def insert_device_state(params):
    mydb = connect_database()
    with mydb.cursor() as mycursor:
        sql = "INSERT INTO device_state (room, type, value, date) VALUES(%s, %s, %s, %s);"
        print(sql, file=sys.stderr)
        #  print(params)
        values = (
            params["room"],
            params["type"],
            params["value"],
            datetime.now()
        )
        mycursor.execute(sql, values)
        mydb.commit()
        return mycursor


# Para obtener la informacion guardada en la tabla device_state
def get_device_state():
    mydb = connect_database()
    r = []
    with mydb.cursor() as mycursor:
        mycursor.execute("SELECT * FROM device_state ORDER BY DATE ASC;")
        myresult = mycursor.fetchall()
        for id, room, type, value, date in myresult:
            r.append({
                "room": room,
                "type": type,
                "value": value,
                "date": str(date)
            })
        mydb.commit()
    return json.dumps(r, sort_keys=True)


# Para guardar la informacion de las habitaciones, su numero asignado y su ultima conexion en la tabla rooms
def insert_room(params):
    mydb = connect_database()
    date_s = datetime.now()
    with mydb.cursor() as mycursor:
        sql = "INSERT INTO rooms (room_num, room_id, type, connection_status, last_connection) VALUES(%s, %s, %s, %s, %s);"
        print(sql, file=sys.stderr)
        #  print(params)
        values = (
            params["room_num"],
            params["room_id"],
            params["type"],
            params["connection_status"],
            datetime.now()
        )
        mycursor.execute(sql, values)
        mydb.commit()
        return mycursor


# Para obtener la informacion de las habitaciones almacenadas
def get_room_state():
    mydb = connect_database()
    r = []
    with mydb.cursor() as mycursor:
        mycursor.execute("SELECT * FROM rooms ORDER BY last_connection ASC;")
        myresult = mycursor.fetchall()
        for room_num, room_id, type, connection_status, last_connection in myresult:
            r.append({
                "room": room_num,
                "room_id": room_id,
                "type": type,
                "value": connection_status,
                "last_connection": str(last_connection)
            })
            mydb.commit()
    return json.dumps(r, sort_keys=True)


def insert_command(params):
    mydb = connect_database()
    date_s = datetime.now()
    with mydb.cursor() as mycursor:
        sql = "INSERT INTO commands (room, command, value, date) VALUES(%s, %s, %s, %s);"
        print(sql, file=sys.stderr)
        #  print(params)
        values = (
            params["room"],
            params["command"],
            params["value"],
            datetime.now()
        )
        mycursor.execute(sql, values)
        mydb.commit()
        return mycursor


app = Flask(__name__)
CORS(app)


# Para hacerse cargo de las peticiones a la base de datos con respecto a la informacion de los sensores
@app.route('/device_state', methods=['GET', 'POST'])
def device_state():
    if request.method == 'POST':
        params = request.get_json()
        if len(params) != 3:
            return {"response": "Incorrect parameters"}
        mycursor = insert_device_state(params)
        return {"response": f"{mycursor.rowcount} records inserted"}
    elif request.method == 'GET':
        mycursor = get_device_state()
        return mycursor


# Para hacerse cargo de las peticiones a la base de datos con respecto a la informacion de las habitaciones
@app.route('/room_list', methods=['GET', 'POST'])
def room_list():
    if request.method == 'POST':
        params = request.get_json()
        mycursor = insert_room(params)
        return {"response": f"{mycursor.rowcount} records inserted"}
    elif request.method == 'GET':
        mycursor = get_room_state()
        if mycursor is None:
            return "[]"
        return mycursor


@app.route('/commands', methods=['GET','POST'])
def commands():
    if request.method == 'POST':
        params = request.get_json()
        mycursor = insert_command(params)
        return {"response": f"{mycursor.rowcount} records inserted"}
    elif request.method == 'GET':
        return ""


HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
app.run(host=HOST, port=PORT, debug=True)

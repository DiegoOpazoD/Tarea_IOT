import socket
import psycopg2
import json
import time



HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 1234       # Puerto en el que se escucha

# Función para cargar la configuración desde el archivo JSON
def cargar_config_db():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

# Función para conectar a la base de datos
def conectar_db():
    config = cargar_config_db()
    db_config = config['db']
    
    try:
        conexion = psycopg2.connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port']
        )
        print("Conexión a la base de datos establecida.")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
        
# Función para desconectar de la base de datos
def desconectar_db(conexion, cursor=None):
    if cursor:
        cursor.close()
        print("Cursor cerrado.")
    if conexion:
        conexion.close()
        print("Conexión a la base de datos cerrada.")

#Funcion para obtener desde la base de datos el protocolo y la capa de transporte
def obtener_protocolo(conexion_db,id_conf):
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT protocolo, capa_transporte FROM Conf WHERE id = %s;", (id_conf,))
        configuracion = cursor.fetchone()
        
        if configuracion:
            return configuracion
        else:
            print(f"No se encontró configuración con id {id_conf}.")
            return None
    except Exception as e:
        print(f"Error durante la consulta: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")

#Funcion para al momento de conectarse a una esp registrarla en la tabla Dev
def guardar_dispositivo(mac_add,conexion_db):
    cursor = None
    try:
        cursor = conexion_db.cursor()
        
        cursor.execute("SELECT device_id FROM Dev WHERE mac_address = %s;", (mac_add,))
        dispositivo = cursor.fetchone()
        
        if dispositivo:
            # Si el dispositivo ya existe, retorno device_id
            device_id = dispositivo[0]
            print(f"El dispositivo con MAC {mac_add} ya está registrado con device_id {device_id}.")
            return device_id
        else:
            # Si no existe, insertamos la MAC y obtenemos el nuevo device_id
            cursor.execute("INSERT INTO Dev (mac_address) VALUES (%s) RETURNING device_id;", (mac_add,))
            device_id = cursor.fetchone()[0]
            conexion_db.commit()  # Confirmar los cambios en la base de datos
            print(f"Dispositivo con MAC {mac_add} registrado con device_id {device_id}.")
            return device_id
    
    except Exception as e:
        print(f"Error al obtener device_id : {e}")
        if conexion_db:
            conexion_db.rollback()  #Hago rollback de las consultas sql 
        return None
    
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")

#Funcion para registrar el log el header de un mensaje recibido
def guardar_log(device_id, msg_id, protocol_id, transport_layer, length, conexion_db):
    cursor = None
    try:
        cursor = conexion_db.cursor()
        
        cursor.execute("""
            INSERT INTO Log (device_id, msg_id, protocol_id, transport_layer, length) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING packet_id;
        """, (device_id, msg_id, protocol_id, transport_layer, length))
        
        # Obtener el packet_id generado
        packet_id = cursor.fetchone()[0]
        conexion_db.commit()  # Confirmar los cambios en la base de datos
        
        print(f"Registro de log guardado para msg_id: {msg_id} Con packet_id : {packet_id}")
        return packet_id
    
    except Exception as e:
        print(f"Error al guardar el log: {e}")
        if conexion_db:
            conexion_db.rollback()  # Deshacer cambios en caso de error
        return None
    
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")

#Funcion para guardar los datos recibidos de un mensaje para la tabla data
def guardar_datos_db():
    return

#funcion para enviar la configuracion de vuelta a una esp conectada
def enviar_configuracion(conn, configuracion):
    protocolo, capa_transporte = configuracion
    
    #lo dejo mientras solo separa como protocolo,capa_transporte
    mensaje = f"{protocolo} , {capa_transporte}"
    
    # Envía el mensaje codificado en UTF-8
    conn.sendall(mensaje.encode('utf-8'))
    
    print(f"Configuración enviada: {mensaje}")

    
conexion_db = conectar_db()
while not conexion_db:
    print("Base de datos no conectada, reintentando conexion")
    time.sleep(3)
    conexion_db = conectar_db()

# Crea un socket para IPv4 y conexión TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen()

    print("El servidor está esperando conexiones en el puerto", PORT)

    while True:
        try:
            conn, addr = s.accept()  # Espera una conexión
            with conn:
                print('Conectado por', addr)
                data = conn.recv(1024)  # Recibe hasta 1024 bytes del cliente
                if data:
                    print("Recibido: ", data.decode('utf-8'))
                    #parse paquete y entender que es, por ahora lo dejo como siempre solicita la configuracion
                    solicita_config = True
                    
                    id_conf = 1
                    configuracion = obtener_protocolo(conexion_db,id_conf)
                    if configuracion:
                        enviar_configuracion(configuracion,conn)
                        
                    else:
                        print("No tengo los datos para responder, espero otro intento de comunicacion")

                    respuesta = "tu mensaje es: " + data.decode('utf-8')
                    conn.sendall(respuesta.encode('utf-8'))  # Envía la respuesta al cliente
        except Exception as e:
                print(f"Error durante la conexión: {e}")
    

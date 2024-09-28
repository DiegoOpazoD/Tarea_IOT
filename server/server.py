import socket
import psycopg2
import json
import time
import struct

## para struct 
# El formato '>I H B' significa:
# - '>': Big-endian (si es little-endian usar '<')
# - 'I': Unsigned int de 32 bits (4 bytes)
# - 'H': Unsigned short de 16 bits (2 bytes)
# - 'B': Unsigned char de 8 bits (1 byte)



HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 1236      # Puerto en el que se escucha


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

#Funcion para obtener desde la base de datos la id de configuracion para la siguiente iteracion
def obtener_id_conf_activa(conexion_db):
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT id_conf_activa FROM ConfActiva;")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"Configuracion activa obtenida con id: {resultado[0]}")
            return resultado[0]  # Retorna el primer elemento de la tupla, que es el id_conf_activa
        else:
            print("No se encontró configuración activa.")
            return None
    except Exception as e:
        print(f"Error durante la consulta: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")

#Funcion para obtener desde la base de datos la id de configuracion para la siguiente iteracion
def obtener_last_msg_id(connexion_db):
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT msg_id FROM log order by msg_id ASC;")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"ultima msg_id obtenido: {resultado[0]+1}")
            return resultado[0]  # Retorna el primer elemento de la tupla, que es el id_conf_activa
        else:
            print("No se encontró msg_id.")
            return 0
    except Exception as e:
        print(f"Error durante la consulta: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")

#Funcion que arma el header para un mensaje
def armar_header(device_mac, msg_id, protocol_id, transport_layer, body_length):
    
    # Asegurarse de que la dirección MAC tenga el tamaño correcto
    if len(device_mac) != 6:
        raise ValueError("La dirección MAC debe tener 6 bytes.")
    
    # Convertir msg_id, protocol_id, transport_layer y body_length a bytes
    msg_id_bytes = msg_id.to_bytes(2, byteorder='big')  # 2 bytes
    protocol_id_bytes = protocol_id.to_bytes(1, byteorder='big')  # 1 byte
    transport_layer_bytes = transport_layer.to_bytes(1, byteorder='big')  # 1 byte
    length_bytes = body_length.to_bytes(2, byteorder='big')  # 2 bytes
    
    # Armar el header
    header = device_mac.encode('utf-8') + msg_id_bytes + protocol_id_bytes + transport_layer_bytes + length_bytes
    
    return header
#Funcion para obtener desde la base de datos el protocolo y la capa de transporte
def obtener_protocolo(conexion_db,id_conf):
    cursor = None

    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT protocol, transport_layer FROM Conf WHERE id = %s;", (id_conf,))
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
        cursor.execute("SELECT id FROM Dev WHERE device_mac = %s;", (mac_add,))
        dispositivo = cursor.fetchone()
        
        if dispositivo:
            # Si el dispositivo ya existe, retorno device_id
            device_id = dispositivo[0]
            print(f"El dispositivo con MAC {mac_add} ya está registrado con device_id {device_id}.")
            return device_id
        else:
            # Si no existe, insertamos la MAC y obtenemos el nuevo device_id
            cursor.execute("INSERT INTO Dev (device_mac) VALUES (%s) RETURNING id;", (mac_add,))
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
            INSERT INTO Log (fk_device_id, msg_id, protocol_id, transport_layer, length) 
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
def guardar_datos_db(conexion_db,packet_id, data ):
    cursor = None
    try:
        cursor = conexion_db.cursor()
        
        timestamp = data.get('timestamp', None)
        batt_level = data.get('batt_level', None)
        temp = data.get('temperature', None)
        pres = data.get('pressure', None)
        hum = data.get('humidity', None)
        co = data.get('CO', None)
        
        amp_x = data.get('amp_x', None)
        amp_y = data.get('amp_y', None)
        amp_z = data.get('amp_z', None)
        
        fre_x = data.get('fre_x', None)
        fre_y = data.get('fre_y', None)
        fre_z = data.get('fre_z', None)
        
        rms = data.get('rms', None)
        
        acc_x = data.get('acc_x', None)
        acc_y = data.get('acc_y', None)
        acc_z = data.get('acc_z', None)
        
        gyr_x = data.get('gyr_x', None)
        gyr_y = data.get('gyr_y', None)
        gyr_z = data.get('gyr_z', None)
        
        # Definir la consulta SQL para insertar los datos en la tabla Data
        query = """
            INSERT INTO Data (
                fk_packet_id, timestamp, batt_level, temp, pres, hum, co,
                amp_x, amp_y, amp_z, fre_x, fre_y, fre_z, rms,
                acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            );
        """
        
        cursor.execute(query, (
            packet_id,
            timestamp, batt_level, temp, pres, hum, co,
            amp_x, amp_y, amp_z, fre_x, fre_y, fre_z, rms,
            acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z
        ))
        
        # Confirmar los cambios
        conexion_db.commit()
        
        print(f"Datos guardados exitosamente para el packet_id: {packet_id}")
        return True
    
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
        if conexion_db:
            conexion_db.rollback()  # Deshacer cambios en caso de error
        return False
    
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")


#funcion para enviar la configuracion de vuelta a una esp conectada
def enviar_configuracion(conn, configuracion,conexion_db):
    capa_transporte , protocolo = configuracion
    capa_transporte_id = 0
    msg_id = obtener_last_msg_id(conexion_db)
    if capa_transporte == "tcp":
        capa_transporte_id = 0
    elif capa_transporte == "udp":
        capa_transporte_id = 1
    else:
        print(f"error capa transporte invalida no es tcp ni udp : {capa_transporte}")
        return
    #lo dejo mientras solo separa como protocolo,capa_transporte
    mensaje = f"{msg_id}{capa_transporte_id}{protocolo}"
    
    print(f"enviando mensaje configuracion : {mensaje}")
    # Envía el mensaje codificado en UTF-8
    conn.sendall(mensaje.encode('utf-8'))
    
    print(f"Configuración enviada: {mensaje}")

#funcion para recibir el mensaje con los datos 
#lo dejo aparte para a futuro manejar aca el rearmar un mensaje de tamaño mayor a 1024 bytes, para iteracion 1 no hace falta
def obtener_mensaje_datos(conn):
    try:
        # Recibe hasta 1024 bytes del cliente
        data = conn.recv(1024)
        
        if data:
            print(f"Mensaje recibido: {data.hex()}")
            return data
        else:
            print("No se recibió ningún dato.")
            return None
    except Exception as e:
        print(f"Error al recibir el mensaje: {e}")
        return None

#Funcion que le hace parse a el body obtenido por el mensaje 
def parse_body(body,protocol_id):
    datos = {}
    timestamp = body[:4] 
    datos['timestamp'] = struct.unpack('I', timestamp)[0]   # Suponiendo que el timestamp es de 4 bytes
    

    if protocol_id == 1:
        batt_level = body[4:5]
        datos['batt_level'] = struct.unpack('<B', batt_level)[0]  # Desempaquetamos como uint8

    elif protocol_id == 2:
        batt_level = body[4:5]
        temp = body[5:6]
        press = body[6:10]
        hum  = body[10:11]
        co = body[11:15]

        datos['batt_level'] = struct.unpack('<B', batt_level)[0]  # Desempaquetamos como uint8
        datos['temperature'] = struct.unpack('<B', temp)[0]      # Desempaquetamos como uint8
        datos['pressure'] = struct.unpack('<I', press)[0]       # Desempaquetamos como uint32 
        datos['humidity'] = struct.unpack('<B', hum)[0]          # Desempaquetamos como uint8
        datos['CO'] = struct.unpack('<I', co)[0]                 # Desempaquetamos como uint32 
    return datos

    ##otros protocolos aca
    # Almacenamos los datos en el diccionario
    








def parse(mensaje):
    header = mensaje[:12]
    mac_add = header[:6]
    msg_id = header[6:8]
    protocol_id = header[8:9]
    transport_layer = header[9:10]
    length = header[10:12]
    body = mensaje[12:]
    
    protocol_id_decodificado = struct.unpack('<B',protocol_id)[0]
    #if protocol_id_decodificado == 0: cambiar cada caso el tañmaño del body


#struct.unpack('I',body)[0] guardao
    dicc_data  = {
        'mac_add' : mac_add.hex(),
        'msg_id' : struct.unpack('<H',msg_id)[0], 
        'protocol_id' : protocol_id_decodificado ,
        'transport_layer' : struct.unpack('<B',transport_layer)[0] ,
        'length' : struct.unpack('<H', length)[0]  ,
        'body': parse_body(body,protocol_id_decodificado),
    }
    return dicc_data
    
conexion_db = conectar_db()
while not conexion_db:
    print("Base de datos no conectada, reintentando conexion")
    time.sleep(3)
    conexion_db = conectar_db()

## para struct 
# El formato '>I H B' significa:
# - '>': Big-endian (si es little-endian usar '<')
# - 'I': Unsigned int de 32 bits (4 bytes)
# - 'H': Unsigned short de 16 bits (2 bytes)
# - 'B': Unsigned char de 8 bits (1 byte)

#test_mensaje = b'\x84\xcc\xa8_!\x88\x01'
#parseado = parse(test_mensaje)
#print(parseado)

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
                data_inicial = conn.recv(1024)  # Recibe hasta 1024 bytes del cliente
                if data_inicial:
                    print("Recibido: ", data_inicial.decode('utf-8'))

                    #parse paquete y entender que es, por ahora lo dejo como siempre solicita la configuracion
                    solicita_config = True
                    id_conf = obtener_id_conf_activa(conexion_db)
                    configuracion = obtener_protocolo(conexion_db,id_conf)
                    if configuracion:
                        print(f"obtuve configuracion: {configuracion}")
                        print("enviando mensaje con configuracion a cliente")
                        enviar_configuracion(conn,configuracion,conexion_db)
                    else:
                        print("No tengo los datos para responder, espero otro intento de comunicacion")
                        continue

                        ############################################### hasta aca esta funcionando ####################################


                    mensaje_datos = obtener_mensaje_datos(conn)
                    #parse paquete y obtener header y body con los datos
                    print(f"Mensaje recibido sin cambiar nada : {mensaje_datos}")
                    parsed_data = parse(mensaje_datos)
                    print(f"Mensaje recibido pasado por parse : {parsed_data}")
                    mac_address = parsed_data['mac_add']
                    #mac_formateada = ':'.join(mac_address[i:i+2] for i in range(0, len(mac_address), 2)).upper()

                    msg_id = parsed_data['msg_id']
                    protocol_id = parsed_data['protocol_id']
                    transport_layer = parsed_data['transport_layer']
                    length = parsed_data['length']
                    body = parsed_data['body']


                    device_id = guardar_dispositivo(mac_address,conexion_db) #guardo el dispositivo con el que estoy recibiendo datos en Dev
                    #device_id identifica el dispositivo que me esta mandando datos y es llave foranea en log
                    packet_id = guardar_log(device_id,msg_id,protocol_id,transport_layer,length,conexion_db) #guardo en log el mensaje que recibi
                    guardar_datos_db(conexion_db,packet_id,body)

        except Exception as e:
                print(f"Error durante la conexión: {e}")
    

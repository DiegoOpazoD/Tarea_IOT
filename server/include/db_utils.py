import json
import psycopg2


def cargar_config_db():
    '''
    Función para cargar la configuración de la base de datos del archivo config.json.
    '''
    with open('include/config.json', 'r') as config_file:
        return json.load(config_file)


def conectar_db():
    '''
    Función para conectar a la base de datos.
    '''
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
        

def desconectar_db(conexion, cursor=None):
    '''
    Función que se desconecta de la base de datos.
    '''
    if cursor:
        cursor.close()
        print("Cursor cerrado.")

    if conexion:
        conexion.close()
        print("Conexión a la base de datos cerrada.")


def obtener_id_conf_activa(conexion_db):
    '''
    Función para obtener la id de la última configuración de la tabla ConfActiva en la base de datos.
    '''
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT id_conf_activa FROM ConfActiva;")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"Configuracion activa obtenida con id: {resultado[0]}")
            return resultado[0] 
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


def obtener_last_msg_id(conexion_db):
    '''
    Función para obtener el último id de la tabla de mensajes en la base de datos.
    '''
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT msg_id FROM log order by msg_id DESC;")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"ultima msg_id obtenido: {resultado[0]+1}")
            return resultado[0]+1 
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


def armar_header(device_mac, msg_id, protocol_id, transport_layer, body_length):
    '''
    Función para armar el header de un mensaje.
    '''
    if len(device_mac) != 6:
        raise ValueError("La dirección MAC debe tener 6 bytes.")
    
    msg_id_bytes = msg_id.to_bytes(2, byteorder='big')  
    protocol_id_bytes = protocol_id.to_bytes(1, byteorder='big') 
    transport_layer_bytes = transport_layer.to_bytes(1, byteorder='big') 
    length_bytes = body_length.to_bytes(2, byteorder='big')  
    header = device_mac.encode('utf-8') + msg_id_bytes + protocol_id_bytes + transport_layer_bytes + length_bytes
    
    return header


def obtener_protocolo(conexion_db, id_conf):
    '''
    Función para obtener el protovolo y la capa de transporte a usar desde la base de datos.
    '''
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


def guardar_dispositivo(mac_add,conexion_db):
    '''
    Función que guarda la MAC address de un dispositivo en la tabla Dev de la base de datos.
    '''
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("SELECT id FROM Dev WHERE device_mac = %s;", (mac_add,))
        dispositivo = cursor.fetchone()
        
        if dispositivo:
            device_id = dispositivo[0]
            print(f"El dispositivo con MAC {mac_add} ya está registrado con device_id {device_id}.")
            return device_id
        
        else:
            cursor.execute("INSERT INTO Dev (device_mac) VALUES (%s) RETURNING id;", (mac_add,))
            device_id = cursor.fetchone()[0]
            conexion_db.commit()  
            print(f"Dispositivo con MAC {mac_add} registrado con device_id {device_id}.")
            return device_id
    
    except Exception as e:
        print(f"Error al obtener device_id : {e}")
        if conexion_db:
            conexion_db.rollback() 
        return None
    
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")


def guardar_log(device_id, msg_id, protocol_id, transport_layer, length, conexion_db):
    '''
    Función que registra el log de un mensaje en la tabla Log de la base de datos.
    '''
    cursor = None
    try:
        cursor = conexion_db.cursor()
        cursor.execute("""
            INSERT INTO Log (fk_device_id, msg_id, protocol_id, transport_layer, length) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING packet_id;
        """, (device_id, msg_id, protocol_id, transport_layer, length))
        
        packet_id = cursor.fetchone()[0]
        conexion_db.commit()  

        print(f"Registro de log guardado para msg_id: {msg_id} Con packet_id : {packet_id}")
        return packet_id
    
    except Exception as e:
        print(f"Error al guardar el log: {e}")
        if conexion_db:
            conexion_db.rollback() 
        return None
    
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")


def guardar_datos_db(conexion_db,packet_id, data ):
    '''
    Función para guardar los datos recibidos en un mensaje dentro de la tabla Data en la base de datos.
    '''
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
        
        conexion_db.commit()        
        print(f"Datos guardados exitosamente para el packet_id: {packet_id}")
        return True
    
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
        if conexion_db:
            conexion_db.rollback()  
        return False
    
    finally:
        if cursor:
            cursor.close()
            print("Cursor cerrado.")


def enviar_configuracion(conn, configuracion,conexion_db):
    '''
    Función que envia la configuración de vuelta a una ESP conectada.
    '''
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

    mensaje = f"{msg_id}{capa_transporte_id}{protocolo}"    
    print(f"enviando mensaje configuracion : {mensaje}")
    conn.sendall(mensaje.encode('utf-8'))    
    print(f"Configuración enviada: {mensaje}")


def obtener_mensaje_datos(conn,transport_layer):
    '''
    Función para recibir el mensaje con los datos dados,
    '''
    try:
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

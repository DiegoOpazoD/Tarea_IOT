import socket
import time

from include.db_utils import *
from include.parser import * 


HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 1236      # Puerto en el que se escucha

    
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
    

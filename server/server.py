import socket
import time
import struct

from include.db_utils import *
from include.esp_msg import * 
from include.esp_connection import * 


HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 1236      # Puerto en el que se escucha
    
conexion_db = conectar_db()
while not conexion_db:
    print("Base de datos no conectada, reintentando conexion")
    time.sleep(3)
    conexion_db = conectar_db()

# Crea un socket para IPv4 y conexión TCP. Esto hay que cambiarlo para la iteración 2.
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen()

    #while True:
    #    conn, addr = s.accept()
    #    with conn:
    #        print('Conectado por', addr)
    #        data_inicial = conn.recv(1024)
    #        print("Me llego un mensaje de data_inicial")
    #        print(f"Recibido:  {data_inicial.decode()}")

    while True:
        try:
            print("El servidor está esperando conexiones en el puerto", PORT)

            conn, addr = s.accept()  
            with conn:
                #print(f"conn: {conn}")
                print('Conectado por', addr)
                data_inicial = conn.recv(1024) 
                if data_inicial:
                    print("Me llego un mensaje de data_inicial")
                    print(f"Recibido:  {data_inicial.decode()}")
                    mac_recibida = data_inicial.decode().split('#')[1]
                    print(f"Mac Recibida: {mac_recibida}")


                    solicita_config = True
                    id_conf = obtener_id_conf_activa(conexion_db)
                    configuracion = obtener_protocolo(conexion_db,id_conf)
                    
                    if configuracion:
                        print(f"obtuve configuracion: {configuracion}")
                        print("enviando mensaje con configuracion a cliente")
                        capa_transporte , protocolo = configuracion
                        conexion_esp = ESP_CONN(capa_transporte,mac_recibida)
                        enviar_configuracion(conn,configuracion,conexion_db)
                        conn.close()
                    else:
                        print("No tengo los datos para responder, espero otro intento de comunicacion")
                        continue
                    capa_transporte , protocolo = configuracion
                    #conexion_esp = ESP_CONN(capa_transporte,mac_recibida)
                    mensaje_datos = conexion_esp.obtener_mensaje_datos()
                    print(f"Mensaje recibido sin cambiar nada : {mensaje_datos}")

                    msg = ESP_MSG(mensaje_datos)
                    print(f"Mensaje recibido pasado por parse : {msg}")
                    msg.save_on_db(conexion_db)

        except Exception as e:
                print(f"Error durante la conexión: {e}")
    

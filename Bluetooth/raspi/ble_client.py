import asyncio
import time
from bleak import BleakClient
from include.db_utils import *
from include.esp_msg import * 

#conf actual
current_conf = "a"

def convert_to_128bit_uuid(short_uuid):
    # Usada para convertir un UUID de 16 bits a 128 bits
    # Los bits fijos son utilizados para BLE ya que todos los UUID de BLE son de 128 bits
    # y tiene este formato: 0000XXXX-0000-1000-8000-00805F9B34FB
    base_uuid = "00000000-0000-1000-8000-00805F9B34FB"
    short_uuid_hex = "{:04X}".format(short_uuid)
    return base_uuid[:4] + short_uuid_hex + base_uuid[8:]

ADDRESS = "84:CC:A8:5F:21:8A"
CHARACTERISTIC_UUID = convert_to_128bit_uuid(0xFF01) # Busquen este valor en el codigo de ejemplo de esp-idf

conexion_db = conectar_db()
while not conexion_db:
    print("Base de datos no conectada, reintentando conexion")
    time.sleep(3)
    conexion_db = conectar_db()


def get_bytes(byte_str):
    return ' '.join(format(byte, '02x') for byte in byte_str)

def enviar_configuracion_v2(conf,conexion_db):

    capa_transporte, protocolo = conf
    if capa_transporte == "tcp":
        capa_transporte_id = '0'
    
    elif capa_transporte == "udp":
        capa_transporte_id = '1'

    msg_id = obtener_last_msg_id(conexion_db)

    msg = f"{capa_transporte_id}{protocolo}{msg_id}#"
    print(msg)
    msg_encoded = msg.encode('utf-8')
    return msg_encoded, capa_transporte_id

async def main(ADDRESS,current_conf):
    while True:
        async with BleakClient(ADDRESS) as client:
            print("se conecto con el dispositivo Bluetooth")
            while True:
                id_conf = obtener_id_conf_activa(conexion_db)
                configuracion = obtener_protocolo(conexion_db,id_conf)
                gui_conf = get_gui_config(conexion_db)[0][0]
                print(f"configuracion gui: {gui_conf}")

                #para cambiar esto hacerlo en el codigo de la GUI, que de ahi se modifique la base de datos
                #current_conf = configuracion
                            
                if gui_conf == 0: #pasarle stop a la db para que se detenga, y para reiniciar llamar al archivo desde GUI
                    while gui_conf != 1:
                        time.sleep(3)
                        print("en el loop")
                        gui_conf = get_gui_config(conexion_db)[0][0]
                
                    id_conf = obtener_id_conf_activa(conexion_db)
                    configuracion = obtener_protocolo(conexion_db,id_conf)

                if configuracion != current_conf:
                    current_conf, comunication_type = configuracion
                    print(f"obtuve configuracion nueva: {configuracion}")
                    print("enviando mensaje con nueva configuracion a servidor")
                
                    conf_to_send = enviar_configuracion_v2(configuracion,conexion_db)
                    print(f"se manda mensaje: {conf_to_send}")
                    await client.write_gatt_char(CHARACTERISTIC_UUID,conf_to_send)

                # si comunication_type es 0 significa que la comunicacion es continua
                if comunication_type == '0':
                    #Pedimos un paquete a esa caracteristica
                    print("pedimos un mensaje")
                    char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    print("msg recivido")
                    print(get_bytes(char_value))
            
                    #se guarda el msg en la estructura ESP
                    msg = ESP_MSG(char_value)
                    print(f"Mensaje recibido pasado por parse : {char_value}")
                    #el msg se guarda en la base de datos
                    msg.save_on_db(conexion_db)

                    #tal vez poner un timer
                    time.sleep(3)
            
                # si comunication_tpye es 1 significa que la comunicacion es discontinua
                elif comunication_type == '1':
                    # se recive el mensaje por primera vez se comporta igual que antes
        
                    #Pedimos un paquete a esa caracteristica
                    print("pedimos un mensaje")
                    char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    print("msg recivido")
                    print(get_bytes(char_value))

                    #se guarda el msg en la estructura ESP
                    msg = ESP_MSG(char_value)
                    print(f"Mensaje recibido pasado por parse : {char_value}")
                    #el msg se guarda en la base de datos
                    msg.save_on_db(conexion_db)

                    time.sleep(3)


                    #salimos de este while
                    break
            
            #salimos tambien del bloque asyn BleackClient asi que se desconecta de la esp
            print("se desconecta con el dispositivo bluetooth")


asyncio.run(main(ADDRESS,current_conf))
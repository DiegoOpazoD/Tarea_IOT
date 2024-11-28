import asyncio
import time
from bleak import BleakClient, BleakScanner
from include.db_utils import *
from include.esp_msg import * 

#conf actual
current_conf = {"84:CC:A8:5F:21:8A":"a",
                "30:C6:F7:29:B1:32":"a"}
#current_conf = "a"

def convert_to_128bit_uuid(short_uuid):
    # Usada para convertir un UUID de 16 bits a 128 bits
    # Los bits fijos son utilizados para BLE ya que todos los UUID de BLE son de 128 bits
    # y tiene este formato: 0000XXXX-0000-1000-8000-00805F9B34FB
    base_uuid = "00000000-0000-1000-8000-00805F9B34FB"
    short_uuid_hex = "{:04X}".format(short_uuid)
    return base_uuid[:4] + short_uuid_hex + base_uuid[8:]

ADDRESS = "a"
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
    return msg_encoded

def convertir_a_formato_mac(texto):
    # Separamos el texto en pares de dos caracteres y luego los unimos con ":" en medio
    return ':'.join([texto[i:i+2].upper() for i in range(0, len(texto), 2)])

# Con esto podemos ver los dispositivos que estan disponibles
async def scan():
    print("Scanning")
    scanner = BleakScanner()
    devices = await scanner.discover()
    devices_filtrados = [device for device in devices if device.name and "gatts_demo" in device.name.lower()]
    print("devices : ", devices_filtrados)
    return devices_filtrados

async def main(ADDRESS,current_conf):
    update_gui_conf(conexion_db,0)
    while True:
        # Ejecutamos la funcion
        devices = await scan()
        update_scanned_esp(conexion_db,devices)
        #print("intentando conectar a mac: " + ADDRESS)

        #revisa que se sleeciono una esp
        esp_actual = get_esp_conf(conexion_db)
        gui_conf = get_gui_config(conexion_db)[0][0]
        print(f"id esp seleccionada : {esp_actual}")
        while esp_actual == 0 or gui_conf == 0:
            time.sleep(3)
            if esp_actual == 0:
                print("Esperando a que se seleccione una esp")
            elif gui_conf == 0:
                print("Esperando a iniciar conexion bluetooth")
            esp_actual = get_esp_conf(conexion_db)
            gui_conf = get_gui_config(conexion_db)[0][0]
            
        ADDRESS = convertir_a_formato_mac(get_esp_mac(conexion_db))
        try:
            async with BleakClient(ADDRESS) as client:
                print("se conecto con el dispositivo Bluetooth")
                while True:
                    #revisar el ADDRES si este cambio salir de aca para que se conecte de 0 de nuevo
                    # new_addres = cosa_bd
                    # if new_addres != ADDRESS
                    #   ADDRESS = new_addres
                    #   break
                    # 
                    new_address = convertir_a_formato_mac(get_esp_mac(conexion_db))
                    print(new_address)
                    if new_address != ADDRESS:
                        ADDRESS = new_address
                        break    

                    id_conf = obtener_id_conf_activa(conexion_db)
                    configuracion = obtener_protocolo(conexion_db,id_conf)
                    gui_conf = get_gui_config(conexion_db)[0][0]
                    print(f"configuracion gui: {gui_conf}")

                    #para cambiar esto hacerlo en el codigo de la GUI, que de ahi se modifique la base de datos
                    #current_conf = configuracion
                            
                    if gui_conf == 0: #pasarle stop a la db para que se detenga, y para reiniciar llamar al archivo desde GUI
                        while gui_conf != 1:
                            time.sleep(3)
                            print("gui_conf 0")
                            gui_conf = get_gui_config(conexion_db)[0][0]

                        # como puede ser que la comunicaion pare aca hay que revisar que no se cambio el address

                        #revisar el ADDRES si este cambio salir de aca para que se conecte de 0 de nuevo
                        # new_addres = cosa_bd
                        # if new_addres != ADDRESS
                        #   ADDRESS = new_addres
                        #   break
                        #
                        new_address = convertir_a_formato_mac(get_esp_mac(conexion_db))
                        if new_address != ADDRESS:
                            #ADDRESS = new_address
                            break

                        id_conf = obtener_id_conf_activa(conexion_db)
                        configuracion = obtener_protocolo(conexion_db,id_conf)  

                    #revisar el diccionario con las dos conf que esten guardadas elegir el addres de ahora
                    capa_transporte, protocolo = configuracion
                    if configuracion != current_conf.get(ADDRESS):
                        current_conf[ADDRESS] = configuracion
                        print(f"obtuve configuracion nueva: {configuracion}")
                        print("enviando mensaje con nueva configuracion a servidor")
                
                        conf_to_send = enviar_configuracion_v2(configuracion,conexion_db)
                        print(f"se manda mensaje: {conf_to_send}")
                        await client.write_gatt_char(CHARACTERISTIC_UUID,conf_to_send)

                    # si comunication_type es udp significa que la comunicacion es continua
                    if capa_transporte == 'udp':
                        #Pedimos un paquete a esa caracteristica
                        print("pedimos un mensaje")
                        char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                        print("msg recivido")
                        print(get_bytes(char_value))
            
                        #se guarda el msg en la estructura ESP
                        msg = ESP_MSG(char_value)
                        print(f"Mensaje recibido pasado por parse : {msg}")
                        #el msg se guarda en la base de datos
                        msg.save_on_db(conexion_db)

                        #tal vez poner un timer
                        time.sleep(3)
            
                    # si comunication_tpye es tcp significa que la comunicacion es discontinua
                    elif capa_transporte == 'tcp':
                        # se recive el mensaje por primera vez se comporta igual que antes
        
                        #Pedimos un paquete a esa caracteristica
                        print("pedimos un mensaje")
                        char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                        print("msg recivido")
                        print(get_bytes(char_value))

                        #se guarda el msg en la estructura ESP
                        msg = ESP_MSG(char_value)
                        print(f"Mensaje recibido pasado por parse : {msg}")
                        #el msg se guarda en la base de datos
                        msg.save_on_db(conexion_db)

                        #mandamos mensaje para cortar comunicacion
                        print("se manda mensaje para cortar la comunicacion")
                        await client.write_gatt_char(CHARACTERISTIC_UUID,"0".encode('utf-8'))

                        client.disconnect()
                        #salimos de este while
                        break

        except Exception as error:
            print(error)
            print("error al conectar")
            
            
        #salimos tambien del bloque asyn BleackClient asi que se desconecta de la esp
        #print("se desconecto con el dispositivo bluetooth")


asyncio.run(main(ADDRESS,current_conf))
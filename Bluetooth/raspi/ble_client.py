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

ADDRESS = "3C:61:05:65:A6:3E"
CHARACTERISTIC_UUID = convert_to_128bit_uuid(0xFF01) # Busquen este valor en el codigo de ejemplo de esp-idf

conexion_db = conectar_db()
while not conexion_db:
    print("Base de datos no conectada, reintentando conexion")
    time.sleep(3)
    conexion_db = conectar_db()


def get_bytes(byte_str):
    return ' '.join(format(byte, '02x') for byte in byte_str)

def enviar_configuracion(client, characteristic, conf):
    await client.write_gatt_char(characteristic, conf)
    return

async def main(ADDRESS):
    async with BleakClient(ADDRESS) as client:
        while True:
            id_conf = obtener_id_conf_activa(conexion_db)
            configuracion = obtener_protocolo(conexion_db,id_conf)

            #para cambiar esto hacerlo en el codigo de la GUI, que de ahi se modifique la base de datos
            current_conf = configuracion
                            
            if configuracion == "stop": #pasarle stop a la db para que se detenga, y para reiniciar llamar al archivo desde GUI
                break
            elif configuracion != current_conf:
                print(f"obtuve configuracion nueva: {configuracion}")
                print("enviando mensaje con nueva configuracion a servidor")
                enviar_configuracion(client,CHARACTERISTIC_UUID,configuracion)

            #Pedimos un paquete a esa caracteristica
            char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print(get_bytes(char_value))
            
            #se guarda el msg en la estructura ESP
            msg = ESP_MSG(char_value)
            print(f"Mensaje recibido pasado por parse : {char_value}")
            #el msg se guarda en la base de datos
            msg.save_on_db(conexion_db)

            #tal vez poner un timer que no se tan rapido??

asyncio.run(main(ADDRESS))
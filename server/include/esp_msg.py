import struct
from db_utils import *
 
# Dentro de struct, el formato '>I H B' significa:
# - '>': Big-endian (si es little-endian usar '<')
# - 'I': Unsigned int de 32 bits (4 bytes)
# - 'H': Unsigned short de 16 bits (2 bytes)
# - 'B': Unsigned char de 8 bits (1 byte)


class ESP_MSG:
    '''
    Clase que representa un mensaje recibido desde una placa ESP32.

    Contiene los siguientes atributos:
        - mac_address: str, la dirección MAC de la placa ESP32 que envió el mensaje.
        - msg_id: int, el identificador del mensaje.
        - protocol_id: int, el identificador del protocolo de comunicación.
        - transport_layer: int, la capa de transporte utilizada.
        - length: int, el tamaño del cuerpo del mensaje.
        - body: bytes, el cuerpo del mensaje.
    '''
    def __init__(self, msg:str) -> None:
        parsed_data = self.parse(msg)
        self.mac_address = parsed_data['mac_add']
        self.msg_id = parsed_data['msg_id']
        self.protocol_id = parsed_data['protocol_id']
        self.transport_layer = parsed_data['transport_layer']
        self.length = parsed_data['length']
        self.body = parsed_data['body']


    def __str__(self) -> str:
        '''
        Representación en formato string del mensaje.

        Retorna un string con los siguientes datos:
            - La dirección MAC de la placa ESP32 que envió el mensaje.
            - El identificador del mensaje.
            - El identificador del protocolo de comunicación.
            - La capa de transporte utilizada.
            - El tamaño del cuerpo del mensaje.
            - El cuerpo del mensaje.
        '''
        return f"MAC: {self.mac_address}, Msg ID: {self.msg_id}, Protocol ID: {self.protocol_id}, Transport Layer: {self.transport_layer}, Length: {self.length}, Body: {self.body}"


    def __parse_body__(body, protocol_id) -> dict:
        '''
        Función que parsea el body en funcióon del protocol_id que se está dando.
        '''
        datos = {}
        timestamp = body[:4] 
        datos['timestamp'] = struct.unpack('I', timestamp)[0]  
        
        if protocol_id == 1:
            batt_level = body[4:5]
            datos['batt_level'] = struct.unpack('<B', batt_level)[0]  

        elif protocol_id == 2:
            batt_level = body[4:5]
            temp = body[5:6]
            press = body[6:10]
            hum  = body[10:11]
            co = body[11:15]

            datos['batt_level'] = struct.unpack('<B', batt_level)[0]  
            datos['temperature'] = struct.unpack('<B', temp)[0]      
            datos['pressure'] = struct.unpack('<I', press)[0]       
            datos['humidity'] = struct.unpack('<B', hum)[0]          
            datos['CO'] = struct.unpack('<f', co)[0]
        elif protocol_id = 3:
            batt_level = body[4:5]
            temp = body[5:6]
            press = body[6:10]
            hum  = body[10:11]
            co = body[11:15]
            amp_x = [15:19]
            amp_y = [19:23]
            amp_z = [23:27]
            fre_x = [27:31]            
            fre_y = [31:35]            
            fre_z = [35:39]
            rms = [39:43]

            datos['batt_level'] = struct.unpack('<B', batt_level)[0]  
            datos['temperature'] = struct.unpack('<B', temp)[0]      
            datos['pressure'] = struct.unpack('<I', press)[0]       
            datos['humidity'] = struct.unpack('<B', hum)[0]          
            datos['CO'] = struct.unpack('<f', co)[0]
            datos['amp_x'] = struct.unpack('<f', amp_x)[0]
            datos['amp_y'] = struct.unpack('<f', amp_y)[0]
            datos['amp_z'] = struct.unpack('<f', amp_z)[0]
            datos['fre_x'] = struct.unpack('<f', fre_x)[0]
            datos['fre_y'] = struct.unpack('<f', fre_y)[0]
            datos['fre_z'] = struct.unpack('<f', fre_z)[0]
            datos['rms'] = struct.unpack('<f', rms)[0]

                             
        elif protocol_id = 4:
            batt_level = body[4:5]
            temp = body[5:6]
            press = body[6:10]
            hum  = body[10:11]
            co = body[11:15]
            acc_x = body[15:8015]
            acc_y = body[8015:16015]
            acc_z = body[16015:24015]
            gyr_x = body[24015:32015]
            gyr_y = body[32015:40015]
            gyr_z = body[40015:48015]
            
            datos['batt_level'] = struct.unpack('<B', batt_level)[0]  
            datos['temperature'] = struct.unpack('<B', temp)[0]      
            datos['pressure'] = struct.unpack('<I', press)[0]       
            datos['humidity'] = struct.unpack('<B', hum)[0]          
            datos['CO'] = struct.unpack('<f', co)[0]

            ######### revisar aca el unpack de float* #################
            datos['acc_x'] = struct.unpack('<f',acc_x)[0]
            datos['acc_y'] = struct.unpack('<f',acc_y)[0]
            datos['acc_z'] = struct.unpack('<f',acc_z)[0]
            datos['gyr_x'] = struct.unpack('<f',gyr_x)[0]
            datos['gyr_y'] = struct.unpack('<f',gyr_y)[0]
            datos['gyr_z'] = struct.unpack('<f',gyr_z)[0]

            
        return datos
        

    def __parse__(self, mensaje) -> dict:
        '''
        Función que parsea el mensaje recibido en un diccionario con sus atributos debidos.
        '''
        header = mensaje[:12]
        mac_add = header[:6]
        msg_id = header[6:8]
        protocol_id = header[8:9]
        transport_layer = header[9:10]
        length = header[10:12]
        body = mensaje[12:]
        
        protocol_id_decodificado = struct.unpack('<B',protocol_id)[0]


        dicc_data  = {
            'mac_add' : mac_add.hex(),
            'msg_id' : struct.unpack('<H',msg_id)[0], 
            'protocol_id' : protocol_id_decodificado ,
            'transport_layer' : struct.unpack('<B',transport_layer)[0] ,
            'length' : struct.unpack('<H', length)[0]  ,
            'body': self.parse_body(body,protocol_id_decodificado),
        }
        return dicc_data
    
    def save_on_db(self, conexion_db):
        '''
        Función que guarda los datos dentro de la base de datos.
        '''
        device_id = guardar_dispositivo(self.mac_address,conexion_db)
        packet_id = guardar_log(device_id, self.msg_id, self.protocol_id, self.transport_layer, self.length, conexion_db) 
        guardar_datos_db(conexion_db, packet_id, self.body)
from server.include.esp_msg import * 
import socket
import struct

HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT_TCP = 1240      # Puerto en el que escucha para mensajes TCP
PORT_UDP = 1250      # Puerto en el que escucha para mensajes UDP
class ESP_CONN:
    '''
        Clase que representa una conexion a una ESP.
        Contiene los siguientes atributos:
            - mac_address:          str, la dirección MAC de la placa ESP32.
            - transport_layer:      str, la capa de transporte utilizada.
            - socket_connection:    socket, socket por donde se esta comunicando con la esp 
            
    '''

    def __innit__(self,transport_layer,mac_address) -> None:
        self.mac_address = mac_address
        self.transport_layer = transport_layer
        if transport_layer == "tcp":
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((HOST,PORT_TCP))
        elif transport_layer == "udp":
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.socket.bind((HOST,PORT_UDP))
        
    def obtener_mensaje_datos(self):
        '''
            Función para recibir el mensaje con los datos dados,
            '''
        if self.transport_layer == "tcp":
            self.socket.listen()
            
            try:
                data = self.socket.recv(1024)
                
                data_length = len(data[12:])
                
                if data:
                    print(f"Mensaje recibido: {data.hex()}")
                    msg_completo = data
                    
                    header = data[:12]
                    mac_add = header[:6]
                    msg_id = header[6:8]
                    protocol_id = header[8:9]
                    transport_layer = header[9:10]
                    length = header[10:12]
                    body = data[12:]
                    
                    protocol_id_decodificado = struct.unpack('<B',protocol_id)[0]

                    dicc_data  = {
                        'mac_add' : mac_add.hex(),
                        'msg_id' : struct.unpack('<H',msg_id)[0], 
                        'protocol_id' : protocol_id_decodificado ,
                        'transport_layer' : struct.unpack('<B',transport_layer)[0] ,
                        'length' : struct.unpack('<H', length)[0]  ,
                        'body': body,
                    }

                    msg_length = dicc_data['length']

                    while data_length < msg_length:
                        data = self.socket.recv(1024)
                        msg_completo += data[12:]
                        data_length += len(data) - 12
                        
                    return msg_completo
                else:
                    print("No se recibió ningún dato.")
                    return None

            except Exception as e:
                print(f"Error al recibir el mensaje: {e}")
                return None

                
        elif self.transport_layer == "udp":
            try:
                msg_completo = ''
                while True:
                    data, addr = self.socket.recvfrom(1024) 
                    data_length = len(data[12:])
                    if data:
                        print(f"Mensaje recibido: {data.hex()}")
                        msg_completo = data
                        
                        header = data[:12]
                        mac_add = header[:6]
                        msg_id = header[6:8]
                        protocol_id = header[8:9]
                        transport_layer = header[9:10]
                        length = header[10:12]
                        body = data[12:]
                        

                        dicc_data  = {
                            'mac_add' : mac_add.hex(),
                            'msg_id' : struct.unpack('<H',msg_id)[0], 
                            'protocol_id' : protocol_id_decodificado ,
                            'transport_layer' : struct.unpack('<B',transport_layer)[0] ,
                            'length' : struct.unpack('<H', length)[0]  ,
                            'body': body,
                        }

                        msg_length = dicc_data.length #total length
                        try:
                            while data_length < msg.length:
                                self.socket.settimeout(10)
                                
                                data,_ = self.socket.recvfrom(1024)
                                msg_completo += data[12:]
                                data_length += len(data) - 12
                        except socket.timeout:
                            #mandar mensaje a ESP para que mande todo de nuevo
                            fallo = True
                        finally:
                            #enviar mensaje final de comunicacion 
                            if fallo:
                                respuesta_cierre = "tamal"
                                self.socket.sendto(respuesta_cierre,addr)
                                
                            else:
                                respuesta_cierre = "tabien"
                                self.socket.sendto(respuesta_cierre,addr)
                                break
                    else:
                        print("No se recibió ningún dato.")
                        return None
                return msg_completo


            except Exception as e:
                print(f"Error al recibir el mensaje: {e}")
                return None


  12            
                
                    
    



from include.esp_msg import * 
import socket
import struct

HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT_TCP = 1240      # Puerto en el que escucha para mensajes TCP
PORT_UDP = 1250      # Puerto en el que escucha para mensajes UDP
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_tcp.bind((HOST,PORT_TCP))
socket_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket_udp.bind((HOST,PORT_UDP))

class ESP_CONN:
    '''
        Clase que representa una conexion a una ESP.
        Contiene los siguientes atributos:
            - mac_address:          str, la dirección MAC de la placa ESP32.
            - transport_layer:      str, la capa de transporte utilizada.
            - socket_connection:    socket, socket por donde se esta comunicando con la esp 
            
    '''

    def __init__(self,transport_layer,mac_address) -> None:
        self.mac_address = mac_address.lower()
        self.transport_layer = transport_layer
        if transport_layer == "tcp":
            self.socket = socket_tcp
            #self.socket.bind((HOST,PORT_TCP))
        elif transport_layer == "udp":
            self.socket = socket_udp
        
    def obtener_mensaje_datos(self):
        '''
            Función para recibir el mensaje con los datos dados,
            '''
        print("abro obtener mensaje datos")
        if self.transport_layer == 'tcp':
            self.socket.listen()
            conn, addr = self.socket.accept()
            msg_completo = ''
            with conn:
                print('Conectado sub socket tcp por', addr)
                try:
                    data = conn.recv(1024)
                    
                    data_length = len(data[12:])
                    
                    if data:
                        #print(f"Mensaje recibido: {data.hex()}")
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

                        #if dicc_data['mac_add'].lower() != self.mac_address:
                        #    print(f"me llego un mensaje de una mac que no es la que esperaba, reiniciando obtener mensaje datos.")
                        #    print(f" self : {self.mac_address} recibida: {dicc_data['mac_add']}")
                        #    return obtener_mensaje_datos
                        
                        msg_length = dicc_data['length']
                        while data_length < msg_length:
                            #print(msg_completo)
                            print(f"se sigue en loop : {data_length} < {msg_length}")
                            #print(f"mensaje completo : {msg_completo} ")
                            data = conn.recv(1024)
                            msg_completo += data[12:]

                            header = data[:12]
                            mac_add_mensaje = header[:6].hex()
                            #if mac_add_mensaje.lower() != self.mac_address:
                            #    print(f"me llego un mensaje de una mac que no es la que esperaba dentro de armar mensaje completo, no considero este mensaje")
                            #    print(f" self : {self.mac_address} recibida: {mac_add_mensaje}")
                            #    continue
                            
                            if(len(data[12:]) < 1000):
                                print(f"largo del mensaje recibido que es muy corto : {len(data[12:])}")
                                print(f"este mensaje parece ser muy corto :  {data[12:]}" )
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

                                print(f"header de mensaje muy corto : {dicc_data['mac_add']} , {dicc_data['msg_id']} , {dicc_data['protocol_id']} , {dicc_data['transport_layer']}, {dicc_data['length']}")




                            data_length = len(msg_completo)
                            
                        return msg_completo
                    else:
                        print("No se recibió ningún dato.")
                        return None

                except Exception as e:
                    print(f"Error al recibir el mensaje: {e}")
                    return None

                
        elif self.transport_layer == 'udp':
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
                        print(f"largo mensaje { msg_length}")
                        fallo = False
                        print(f"antes de entrar al loop : {data_length} < {msg_length}")
                        try:
                            while data_length < msg_length:
                                print("entro a loop")
                                self.socket.settimeout(5)
                                print(f"se sigue en loop : {data_length} < {msg_length}")
                                data,_ = self.socket.recvfrom(1024)
                                msg_completo += data[12:]
                                data_length = len(msg_completo)
                        except socket.timeout:
                            print("ocurrio timeout")
                            #mandar mensaje a ESP para que mande todo de nuevo
                            fallo = True
                        finally:
                            self.socket.settimeout(None)
                            #enviar mensaje final de comunicacion 
                            if fallo:
                                respuesta_cierre = "tamal".encode()
                                self.socket.sendto(respuesta_cierre,addr)
                                
                            else:
                                respuesta_cierre = "tabien".encode()
                                self.socket.sendto(respuesta_cierre,addr)
                                break
                    else:
                        print("No se recibió ningún dato.")
                        return None
                return msg_completo


            except Exception as e:
                print(f"Error al recibir el mensaje: {e}")
                return None
         
                
                    




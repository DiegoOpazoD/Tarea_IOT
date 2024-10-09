HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT_TCP = 1240      # Puerto en el que se escucha
PORT_UDP = 1250
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
        elif transport_layer == "udp":
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
        self.socket.bind((HOST,PORT))



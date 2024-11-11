from peewee import *
from models import *

db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'iot_db'
}

def insert_conf(protocol, transport_layer):
    Conf.insert(
        protocol=protocol,
        transport_layer=transport_layer
    ).execute()
def insert_conf_activa(id_conf):
    ConfActiva.insert(
        id_conf_activa=id_conf,
    ).execute()
    

def populate_conf():
    # Definir los posibles transport layers
    transport_layers = ["tcp", "udp"]
    # Definir los 5 posibles protocolos (0-4)
    protocols = [0, 1, 2, 3, 4]
    
    # Inserta todos los pares protocolo/capa de transporte
    for transport_layer in transport_layers:
        for protocol in protocols:
            insert_conf(transport_layer, str(protocol))  # Inserta cada par

if __name__ == "__main__":
    # Llenar la tabla Conf con todos los pares posibles
    populate_conf()
    print("Tabla Conf llenada con éxito")
    insert_conf_activa(1)
    print("seteada conf_activa a id 1 (tcp , P0)")
    
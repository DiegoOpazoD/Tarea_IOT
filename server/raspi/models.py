from peewee import Model, PostgresqlDatabase, ForeignKeyField, AutoField, IntegerField, FloatField, CharField

# Configuracion de la base de datos
db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'iot_db'
}
db = PostgresqlDatabase(**db_config)

class BaseModel(Model):
    class Meta:
        database = db
# Se definen los modelos
# Tabla Dev: Almacena los dispositivos con los que ha tenido contacto
class Dev(BaseModel):
    device_mac = CharField(unique=True, max_length=12)  # 6 bytes en formato hex (12 caracteres)

# Tabla Log: Llevará un registro de todos los mensajes recibidos
class Log(BaseModel):
    packet_id = AutoField()                               # Identificador del paquete, serial auto-incremental
    fk_device_id = ForeignKeyField(Dev, backref='logs')   # Relacionado con el dispositivo (device_id)
    
    # Columnas para la información del header
    msg_id = IntegerField()                               # Identificador de mensaje (2 bytes)
    protocol_id = IntegerField()                          # Protocolo (1 byte)
    transport_layer = IntegerField()                      # Capa de transporte (1 byte)
    length = IntegerField()                               # Longitud del mensaje (2 bytes)



# Se crean las tablas
db.create_tables([Dev,Log])
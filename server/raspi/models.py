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
# Tabla Data: Almacena la data obtenida por la RasPi
class Data(BaseModel):
    fk_packet_id = ForeignKeyField(Log, backref='data')   # Llave foránea que referencia a Log (packet_id)
    
    # Columnas de datos (sin restricciones)
    timestamp = IntegerField(null=True)                   # Marca de tiempo (4 bytes)
    batt_level = IntegerField(null=True)                  # Nivel de batería (1 byte)
    temp = IntegerField(null=True)                        # Temperatura (1 byte)
    pres = IntegerField(null=True)                        # Presión (4 bytes)
    hum = IntegerField(null=True)                         # Humedad (1 byte)
    co = FloatField(null=True)                            # CO (4 bytes)
    
    amp_x = FloatField(null=True)                         # Aceleración en X (4 bytes)
    amp_y = FloatField(null=True)                         # Aceleración en Y (4 bytes)
    amp_z = FloatField(null=True)                         # Aceleración en Z (4 bytes)
    
    fre_x = FloatField(null=True)                         # Frecuencia en X (4 bytes)
    fre_y = FloatField(null=True)                         # Frecuencia en Y (4 bytes)
    fre_z = FloatField(null=True)                         # Frecuencia en Z (4 bytes)
    
    rms = FloatField(null=True)                           # Valor RMS (4 bytes)
    
    acc_x = FloatField(null=True)                         # Aceleración en X (8000 bytes)
    acc_y = FloatField(null=True)                         # Aceleración en Y (8000 bytes)
    acc_z = FloatField(null=True)                         # Aceleración en Z (8000 bytes)
    
    gyr_x = FloatField(null=True)                         # Giroscopio en X (8000 bytes)
    gyr_y = FloatField(null=True)                         # Giroscopio en Y (8000 bytes)
    gyr_z = FloatField(null=True)                         # Giroscopio en Z (8000 bytes)




# Se crean las tablas
db.create_tables([Dev,Log,Data])
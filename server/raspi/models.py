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



# Se crean las tablas
db.create_tables([Dev])
from peewee import *
from models import *

db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'iot_db'
}

def insert_user(username):
    User.insert(
        username=username
    ).execute()

if __name__ == "__main__":
    username = input("Ingrese el nombre de usuario: ")
    insert_user(username)
    print("Usuario creado con éxito")
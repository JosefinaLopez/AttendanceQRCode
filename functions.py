
import pyodbc
import base64

#Convierte la foto en bytes
def ConvertPhoto(foto):
  with open(foto, "rb") as f:
    return f.read()

#Convierte el archivo bytes a base64 para mostrarlo en la pagina
def ViewPhoto(Varbinary):
  img = base64.b64encode(Varbinary).decode('utf-8')
  return img

#Convierte la foto de bytes a varbinary para insertar en BD
def ConvertVarbinary(byte):
  uwu = pyodbc.Binary(byte)
  return uwu;


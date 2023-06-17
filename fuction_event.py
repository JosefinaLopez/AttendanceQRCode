from datetime import datetime
import datetime
from flask import jsonify
from conexion import connection 
#!Libreria de Cola
from collections import  deque
from dateutil import parser


#? Idea a implementar = en cambio de que la bd este consultando el evento, cada minuto, debo evitar el gasto de recursos
#? hacer una cola que guarde los eventos y luego que solo se muestre y comparen

db = connection('JOSEFINALOPEZ\JOSEFINALOPEZ','Student_Attendance')
cursor = db.cursor()

#!Se crea la cola
cola_event = deque()

#!Metodo para agregar eventos
def AddCola (evento):
    cola_event.append(evento)

#!Metodo para guardar eventos de la bd y agregarlos a la cola
def ColaEventos(dia):
    
    eventos = cursor.execute("""
    SELECT
    cl.NameClasse AS Clase,
    CONVERT(VARCHAR(10), h.StartTime, 108) AS Hora_Inicio,
    CONVERT(VARCHAR(10), h.EndTime, 108) AS Hora_Final,
    d.NameDay AS Dia
	FROM School_Hours h
	INNER JOIN Assignment a ON a.Classes_Id = h.Id
	INNER JOIN Classes cl ON cl.Id = a.Classes_Id
	INNER JOIN Days d ON d.Id = h.Day_Id
	WHERE d.NameDay = ?
                
                """,dia).fetchall()
    
    #!Recorre el resultado y lo agrega a la cola xd
    for evento in eventos:
        AddCola(evento) 
        #print(evento) 

def CompararEvento(hora_actual):

    clase_actual = None
    inicio_actual = None
    final_actual = None

    for evento in cola_event:
        
        # Se fija el rango de la hora que se mostrará el evento
        clase_actual = evento[0]
        inicio_actual = evento[1]
        final_actual = evento[2]
        final = evento[2]

    if inicio_actual is not None and final_actual is not None and hora_actual != '':
        _hora_actual = getTimestamp(hora_actual)
        inicio_actual = getTimestamp(inicio_actual)
        final_actual = getTimestamp(final_actual)
        # Convertir a timestamp Unix
        #final_actual = datetime.strftime(final_actual,'%H:%M:%S').time()
        #! 20:28:00  >=  20:23:00  - True  20:23:00 <= 22:59:00 - True
        print(final_actual)
        if _hora_actual >= inicio_actual and _hora_actual <= final_actual:
            return jsonify({'clase': clase_actual, 'final': final})
        else:
            return jsonify({'clase': 'Aun no hay', 'final': '00:00'})
    else:
            return jsonify({'clase': 'XDDDD', 'final': '00:00'})



#?print("No hay eventos por ahora ¯\_(ツ)_/¯")  
def getTimestamp(hora):
    dia_actual = datetime.datetime.now().date()
    tiempo = datetime.datetime.strptime(hora, "%H:%M:%S").time()
    fecha_tiempo = datetime.datetime.combine(dia_actual, tiempo)

    return int(fecha_tiempo.timestamp())
if __name__ == "__main__":
    """
    #?Comprobando si funciona jja 
    print("☆*: .｡. o(≧▽≦)o .｡.:*☆" *2)
    dia = input("Ingrese el dia de hoy: ")
    hora_actual = input("Ingrese la hora actual:")
    print("☆*: .｡. o(≧▽≦)o .｡.:*☆" *2)

    print("\n")

    ColaEventos(dia)
    CompararEvento(hora_actual) 
    """


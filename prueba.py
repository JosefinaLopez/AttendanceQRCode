from conexion import connection 
#!Libreria de Cola
from collections import  deque

db = connection('JOSEFINALOPEZ\JOSEFINALOPEZ','Student_Attendance')
cursor = db.cursor()

#!Se crea la cola
cola_event = deque()

#!Metodo para agregar eventos
def AddCola (evento):
    cola_event.append(evento)

#!Metodo para guardar eventos de la bd y agregarlos a la cola
def TomarEventos(dia):
    
    eventos = cursor.execute("""
    SELECT
	c.NameClasse AS Clase,
	CONVERT(VARCHAR(25), h.StartTime,100) AS Hora_Inicio,
    CONVERT(VARCHAR(25),h.EndTime,100) AS Hora_Final,
	d.NameDay AS Dia
	FROM School_Hours h
	INNER JOIN Classes c ON c.Id = h.Class_Id
	INNER JOIN Days d ON d.Id = h.Day_Id
	WHERE d.NameDay = ?
                
                """,dia).fetchall()
    
    #!Recorre el resultado y lo agrega a la cola xd
    for evento in eventos:
        AddCola(evento)  

def CompararEvento(hora_actual):
    
    for evento in cola_event:
        if evento[1] <= hora_actual or evento[2] <= hora_actual:
            info = (f"""
                    
                    Informacion de Evento
                    
                    ( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)
                    
                    Evento = {evento[0]}
                    Finaliza a las = {evento[2]}
                    
                """)
            centro = info.center(50)
            print(centro)
            print("\n")

        else: 
            print("No hay eventos por ahora ¯\_(ツ)_/¯")  
        
if __name__ == "__main__":
    #?Comprobando si funciona jja 
    print("☆*: .｡. o(≧▽≦)o .｡.:*☆" *2)
    dia = input("Ingrese el dia de hoy: ")
    hora_actual = input("Ingrese la hora actual:")
    print("☆*: .｡. o(≧▽≦)o .｡.:*☆" *2)

    print("\n")

    TomarEventos(dia)
    CompararEvento(hora_actual)


from conexion import connection 
import datetime
from flask import request, flash

db = connection('JOSEFINALOPEZ','Student_Attendance')

def mostrar(hora_actual):
    cursor = db.cursor()
    #Se toma el dia de hoy del sistema
    now = datetime.datetime.now()
    #Se pasa un dia ej : Saturdayxd
    dia_actual = now.strftime("%A")
    
    #Este procedimiento almacenado separa los dias xd
    day = cursor.execute("EXEC usp_DiasClases ?", (hora_actual)).fetchall()
    #Se crea el arreglo 
    clase_actual = []
    print(day)
    cla = False
   
    for dia in day:
        flash("iww")
        #compara el dia de la bd con el dia actual
        if dia[1] == dia_actual:
            #tomo como parametro ese dia para poder extraer mas informacion de la clase
            actual = cursor.execute("SELECT NombreMateria,HoraInicio,HoraFinal FROM Materia WHERE NombreMateria = ?",(dia[2])).fetchall()
            #recorro la salida de la consulta y la agrego al arreglo
            for clase in actual:
                clase_actual.append(clase)
            
    for clas in clase_actual:
        owo = clas[0]
        xd = clas[2]
        cla = True
        print("resultado metodo view: "+ str(owo) + str(xd))
    cursor.close()
    print(clase_actual)

    # Si no existe v:
    if not cla:
        flash("uwu")
        return (None, None) 
    # De lo contrario 
    else: 
        return (str(owo), str(xd))

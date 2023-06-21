from flask import jsonify
from conexion import connection

db = connection('JOSEFINALOPEZ\JOSEFINALOPEZ','Student_Attendance')
cursor = db.cursor()

def Asistencia(fecha, codigo, clase):
    #print(codigo)
    #print(fecha)
    #print(clase)
    cursor.execute("EXEC usp_Register_Attendance ?,?,?",(str(fecha),str(codigo),str(clase)))
    cursor.commit()
    print("Funciono")
    
def MostrarAsistenciaActual(clase, fecha):
    xd = cursor.execute("EXEC usp_ViewAsistencia ?,?", (str(clase),str(fecha))).fetchall()   
    return xd

def viewasis(clase,fecha):
    attendance_data = []
    consul = cursor.execute("EXEC usp_ViewAsistencia ?,?", (str(clase),str(fecha))).fetchall()
    if len(consul) != 0:
        for attendance in consul:
            attendance_data.append({
            'id': attendance[1],
            'student': attendance[2],
            'carnet': attendance[3],
            'gmail': attendance[4],
            'telefono': attendance[5],
        })
        return jsonify({'attendance': attendance_data, 'confirmacion': 'Asistencia tomada exitosamente'})
    else:  
        return jsonify({
            'id': '',
            'student': '',
            'carnet': '',
            'gmail': '',
            'telefono': '',
            'confirmacion': ''
        })
    
def idprox(tbla):
    idh = cursor.execute(f"SELECT MAX(Id) FROM {tbla}").fetchone()
    if idh[0] is None:
        idh = 1
        print("aquiiiiii")
    else:
        idh = int(idh[0])+1
        print(idh)
    return idh

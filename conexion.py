import pyodbc

def connection(server, bd):
    # Conexión a la base de datos
    conn = pyodbc.connect('Driver={SQL Server};'
                        f'Server={server};'
                        f'Database={bd};'
                        'Trusted_Connection=yes;')

    return conn 

def Asistencia(fecha, codigo, clase):
    db = connection('JOSEFINALOPEZ', 'Student_Attendance')
    cursor = db.cursor()
    print(codigo)
    print(fecha)
    print(clase)
    cursor.execute("EXEC usp_Register_Attendance ?,?,?",(str(fecha),str(codigo),str(clase)))
    cursor.commit()
    print("Funciono")

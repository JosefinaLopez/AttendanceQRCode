from conexion import connection

db = connection('JOSEFINALOPEZ\JOSEFINALOPEZ','Student_Attendance')
cursor = db.cursor()

def long_pag(limit, inic,tbl):
    long = cursor.execute(f"SELECT COUNT(1) FROM {tbl}").fetchall()[0]
    
    if inic >= int(long):
        print('No hay nada aqui') 
    
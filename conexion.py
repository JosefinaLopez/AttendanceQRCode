import pyodbc

def connection(server , bd):
    # Conexión a la base de datos
    conn = pyodbc.connect('Driver={SQL Server};'
                        'Server=JOSEFINALOPEZ\CARMEN;'
                        f'Database={bd};'
                        'Trusted_Connection=yes;')

    return conn 

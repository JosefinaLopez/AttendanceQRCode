from os import remove
from flask import Flask, render_template, redirect, session, request, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
from flask_session import Session
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from conexion import connection 
from cloud_firebase import Send_QR, Link_Img,Link_Download

app = Flask(__name__)

db = connection('JOSEFINALOPEZ','Student_Attendance')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

        
 #Principal       
@app.route('/', methods=["GET", "POST"])
def index():
    # if request.method == "GET":
    #Delete_Img()
   return render_template("index.html")



#Region de Registros
@app.route("/RegisterStudent",methods=["GET","POST"])
def registerA():

   cursor = db.cursor()
      
   query = "SELECT Id, NombreCarrera FROM Carrera"
   rows = cursor.execute(query).fetchall()

   Año = "SELECT Id, NombreAño FROM Año_Lectivo"
   row = cursor.execute(Año).fetchall()
   
   #Obtiene el ultimo Id Registrado y le suma una 
   comprobar_code = "SELECT MAX(Id) FROM Estudiantes"
   code_id = cursor.execute(comprobar_code).fetchone()[0]
   print(code_id)

   code = 0;
   if(code_id is None):
     code = 1
     codigo = f"ESTUDI0001"
   else:
     code = code_id+1;
   print(code)

   #ESTU0001    
   if(code < 10):
    codigo = f"ESTUD000{code}"
   elif(code < 100):
    #ESTU099
    codigo = f"ESTUD0{code}"
    #ESTU999
   elif(code< 1000):
    codigo = f"ESTUD{code}"   

   if request.method == "POST":

      name = request.form.get("Nombre")
      carnet = request.form.get("Carnet")
      correo = request.form.get("Correo")
      telefono = request.form.get("Telefono")
      carrera = request.form.get("Carrera")
      año = request.form.get("Año")
      
      #Se crea la imagen de Codigo QR
      qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
      #El nombre a poner
      qr.add_data(codigo)
      #Se genera el nuevo estilo del codigo QR
      img_QR = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
      
      #QR = Image.open(f"{carnet}"+".png")
      ruta = f"static/img/QR/{codigo}.png"
      img_QR.save(ruta)
         
      #Que me arroje el primer resultado 
      verificar = cursor.execute("SELECT *FROM Estudiantes WHERE carnet = ?",(carnet)).fetchone()
      print(verificar)
      
      
      if verificar is None:
         #Se envia a Firebase Storage 
         Send_QR(f"{codigo}",ruta)
         #Se obtiene el enlace para poder visualizar la imagen
         img = Link_Img(f"{codigo}")

         cursor.execute("INSERT INTO Estudiantes (Nombre,Carnet,Correo,Telefono,QR_Img,Carrera_Id,Año_Lectivo_Id) VALUES (?,?,?,?,?,?,?)",
                       (name,carnet,correo,telefono,img,carrera ,año))
         cursor.commit()
         
        #Se remueve el codigo qr que se guardo en esa ruta 
         remove(ruta)
         return render_template("Alumnos.html",carreras = rows, Años = row)
      else: 
         
         return render_template("Alumnos.html",carreras = rows, Años = row)
   else:
     return render_template("Alumnos.html",carreras = rows,Años = row)


@app.route('/RegistroDocentes', methods=["GET", "POST"])
def clases():
   cursor = db.cursor()
   dep = cursor.execute("SELECT Id, NombreDepartamento FROM Departamento").fetchall()
   clases = cursor.execute("SELECT Id, NombreMateria FROM Materia").fetchall()
   #print(dep)
   print(clases)
   nombre = request.form.get("Nombre")
   correo = request.form.get("Correo")
   telefono = request.form.get("Telefono")
   dtp_id = request.form.get("Departamento")
   clase = request.form.get("Clase")
   
    #Obtiene el ultimo Id Registrado y le suma una 
   comprobar_code = "SELECT MAX(Id) FROM Docentes"
   code_id = cursor.execute(comprobar_code).fetchone()[0]
   print(code_id)

   code = 0;
   if(code_id is None):
     code = 1
     codigo = f"DOCENT0001"
   else:
     code = code_id+1;
   print(code)

   #DOCENT0001    
   if(code < 10):
    codigo = f"DOCENT000{code}"
   elif(code < 100):
    #DOCENT099
    codigo = f"DOCENT0{code}"
    #DOCENT999
   elif(code< 1000):
    codigo = f"DOCENT{code}"    

   #Se crea la imagen de Codigo QR
   qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
   #El nombre a poner
   qr.add_data(codigo)
   #Se genera el nuevo estilo del codigo QR
   img_QR = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
      
   #QR = Image.open(f"{carnet}"+".png")
   ruta = f"static/img/QR/{codigo}.png"
   img_QR.save(ruta)

   if request.method == "POST":
      verificar = cursor.execute("SELECT NombreDocente FROM Docentes WHERE Correo = ?", (correo)).fetchone()
      if verificar is None:
         #Se envia a Firebase Storage 
         Send_QR(f"{codigo}",ruta)
         #Se obtiene el enlace para poder visualizar la imagen
         img = Link_Img(f"{codigo}")

         cursor.execute("INSERT INTO Docentes (NombreDocente,Correo,Telefono,QR_img,Materia_Id,Departamento_Id) VALUES(?,?,?,?,?,?)",
                        (nombre,correo,telefono,img,clase,dtp_id))
         cursor.commit()
         cursor.close()
         print("Registro existoso")
         return render_template("Maestros.html", dep = dep, clases = clases)
      else: 
         print("Registro Ya Existe") 
         return render_template("Maestros.html",dep = dep, clases = clases)       
   else:  
    return render_template("Maestros.html",dep = dep , clases = clases)


@app.route('/RegistroClases', methods=["GET", "POST"])
def maestros():
   cursor = db.cursor()
   carrera = cursor.execute("SELECT Id, NombreCarrera FROM Carrera").fetchall()
   lugar = cursor.execute("SELECT Id, NombreLugarMaterias FROM Lugar_Materias").fetchall()
  
   #Variables
   nombre = request.form.get("Nombre")
   #Convierte la seleccion en listas
   fecha = request.form.getlist("Dias")
   #Las convierte en un str con comas para insertar en la bd
   dias = ','.join(fecha)
   hinit = request.form.get("HoraInicio")
   hfini = request.form.get("HoraFinal")
   carrera_id = request.form.get("Carrera_Id")
   lugar_id =request.form.get("Lugar_Id")

   if request.method=="POST":
      verificar = cursor.execute("SELECT NombreMateria FROM Materia WHERE NombreMateria = ?",(nombre)).fetchone()
      print(verificar)
      
      if verificar is None:
         cursor.execute("INSERT INTO Materia (NombreMateria,Dias,HoraInicio,HoraFinal,Carrera_Id,Lugar_Id)"
                        "VALUES (?,?,?,?,?,?)",(nombre,dias,hinit,hfini,carrera_id,lugar_id))
         cursor.commit()
         cursor.close()
         print("Registro exitoso")
         return render_template("Materias.html", carreras = carrera , lugares = lugar)
      else:
         print("Registro existente") 
         return render_template("Materias.html", carreras = carrera , lugares = lugar)

   return render_template("Materias.html", carreras = carrera , lugares = lugar)


@app.route('/Asistencia', methods=["GET", "POST"])
def asistencia():
    if request.method=="GET":
       
     return render_template("QRScanner.html")  
    
    

#Region de Views O para Mostrar los Registros xd
@app.route('/MostrarAlumno', methods=["GET", "POST"])
def viewA():
   cursor = db.cursor()
   #Procedimiento almacenado que muestra informacion de estudiantes
   consulta = cursor.execute("EXEC usp_ViewStudent").fetchall()
   
   #Verifica si existe o no
   if len(consulta) == 0:
      return render_template("index.html")
   else:
      cursor.close()
      return render_template("result.html", Info = consulta)

#Editar Registros






#Eliminar Registros







#Funcionalidades Propias XD

@app.route('/Search', methods=["GET", "POST"])
def search():
     cursor = db.cursor()
     if request.method=="POST":
       dato = request.form.get("Search")
       print(dato)
       query = cursor.execute("EXEC Search ?", (dato)).fetchone()
       print(len(query))
       print(query)
       cursor.close()

       if query is None:
          print("No hay ningun registro")
          return render_template("index.html")

       elif len(query) == 8:
        print("Es Estudiante")
        return render_template("result.html", Info = query, query = 1)
       
       elif len(query) == 9:
          print("Es Docente")
          return render_template("result.html", Info = query, query = 1)
       
       elif len(query) == 6:
          print("Es una clase") 
          return render_template("result.html", Info = query, query = 1)  

       return render_template("index.html")  


@app.route('/Imagen/<codigo>', methods=["GET", "POST"])
def imagen(codigo):
   cursor = db.cursor()
   if request.method =="GET":
      Alumnos = cursor.execute("SELECT QR_Img FROM Estudiantes WHERE Codigo = ?",(codigo)).fetchone()

      if Alumnos is None:
         Docentes = cursor.execute("SELECT QR_Img FROM Docentes WHERE Codigo = ?", (codigo)).fetchone()
         url = Docentes[0]
         img = Link_Download(url)
         print(f"Es docente {Docentes}")
      else:   
         url = Alumnos[0]
         img = Link_Download(url)
         print(f"Es Alumno {Alumnos}")

      if Alumnos is None and Docentes is None:
         print("No hay nada aqui")   

      #img = Link_Download("https://firebasestorage.googleapis.com/v0/b/project-qrimg.appspot.com/o/qr%2FESTUD0001?alt=media")
   return send_file(img, download_name=f"{codigo}.png")



#Region Login 
@app.route('/Login', methods=["GET", "POST"])
def login():
   cursor = db.cursor()
   if request.method == "POST":

      username = request.form.get("Username")
      password = request.form.get("Password")


      verificar = cursor.execute("SELECT *FROM Usuario WHERE username = ?", (username)).fetchone()
      if verificar is None:
         print("No existe el usuario")
         return render_template("Login.html")
      elif (check_password_hash(verificar[2],password)):
         print("Contraseña Incorrecta")
         return render_template("Login.html")
      else:
         session["user_id"] = verificar[0]
         session["username"] = verificar[1]
         return render_template("index.html", usser = username)
            
   return render_template("login.html")


@app.route('/RegistroUsuario', methods=["GET", "POST"])
def register():
      cursor = db.cursor()
      roles = cursor.execute("SELECT Id, NombreRol FROM Rol").fetchall()
      print(roles)

      if request.method == "POST":
        username = request.form.get("Username")
        password = request.form.get("Password")
        rol = request.form.get("Rol")
        confirm = request.form.get("Password-Confirm")

        hash = generate_password_hash(password)

        verificar = cursor.execute("SELECT *FROM Usuario WHERE username = ?",(username)).fetchone()

        if verificar is None:
           cursor.execute("INSERT INTO Usuario (Username, Password, Id_Rol) VALUES(?,?,?)",(username,hash,rol))
           cursor.commit()
           print("Usuario Registrado Exitosamente")
           return render_template("Login.html", roles = roles)
        else:
           print("Usuario Existente")   
           return render_template("Register.html", roles = roles)
      return render_template("Register.html" , roles = roles)


@app.route('/Logout', methods=["GET", "POST"])
def logout():
   session.clear() 
   return render_template("login.html")

 
if __name__ == "__main__":
    app.run(debug=True)
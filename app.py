from os import remove
from flask import Flask, render_template, redirect, session, request, flash, send_file, url_for,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import datetime
from flask_session import Session
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from conexion import connection , Asistencia, MostrarAsistenciaActual
from cloud_firebase import Send_QR, Link_Img,Link_Download

app = Flask(__name__)

db = connection('JOSEFINALOPEZ','Student_Attendance')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=['GET'])
def index():
   return render_template("index.html")

@app.route('/horario_actual', methods=['GET'])
def horario_actual():
   hora_actual = request.args.get('time', '')
   dia_actual = datetime.datetime.now().strftime("%A")
   cursor = db.cursor()

   now = datetime.datetime.now()
   current_time = now.strftime("%I:%M%p")

   if hora_actual is None or len(hora_actual) == 0:
      hora_actual = current_time
   else:
      hora_actual = hora_actual    
   info = cursor.execute("EXEC usp_InfoIndex ?,?", (dia_actual, hora_actual)).fetchall()
   clase_actual = None
   final_actual = None
   if len(info) !=0 :
   
      for clase, inicio, final in info:
         clase_actual = clase
         final_actual = final
         cursor.close()
      if clase_actual is not None:
         return jsonify({'clase': clase_actual, 'final': final_actual})
      else:
         return jsonify({'clase': 'Aún no hay', 'final': '00:00'})
   cursor.close()
   return jsonify({'clase': 'Aún no hay', 'final': '00:00'})


@app.route("/RegistroAlumno",methods=["GET","POST"])
def registerA():

   cursor = db.cursor()
      
   #Obtiene el ultimo Id Registrado y le suma una 
   comprobar_code = "SELECT MAX(Id) FROM Students"
   code_id = cursor.execute(comprobar_code).fetchone()[0]
   print(code_id)

   code = 0
   if code_id is None:
      code = 1
      codigo = f"STUDNT0001"
   else:
      code = code_id+1
   #print(code)
   #ESTU0001    
   if code < 10:
      codigo = f"STUDNT000{code}"
   elif code < 100:
   #ESTU099
      codigo = f"STUDNT00{code}"
   #ESTU999
   elif code < 1000:
      codigo = f"STUDNT0{code}" 
   else:
      codigo = f"STUDNT{code}"  

   if request.method == "POST":

      name = request.form.get("Nombre")
      carnet = request.form.get("Carnet")
      correo = request.form.get("Correo")
      telefono = request.form.get("Telefono")
      carrera = request.form.get("Carrera")
      año = request.form.get("Año")
      genero = request.form.get("Genero")
      codigo_update = request.form['Codigo']
      
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
      verificar = cursor.execute("SELECT *FROM Students WHERE Code = ?",(codigo_update)).fetchone()
      print(verificar)
      
      #Si el registro no existe se agrega, y si, si existe, se edita xd
      if verificar is None:
         #Se envia a Firebase Storage 
         Send_QR(f"{codigo}",ruta)
         #Se obtiene el enlace para poder visualizar la imagen
         img = Link_Img(f"{codigo}") 

         cursor.execute("INSERT INTO Students (NameStudent,Student_Card,Gender_Id,[E-Mail],Phone,QR_Img,Career_Id,School_Year_Id) VALUES(?,?,?,?,?,?,?,?)",
         (name,carnet,genero,correo,telefono,img,carrera ,año))
         cursor.commit()
         flash("Successful registration")
      #Se remueve el codigo qr que se guardo en esa ruta 
         remove(ruta)
         return redirect("/Alumnos")
      else: 
         cursor.execute("UPDATE Students SET NameStudent = ?, Student_Card = ?,Gender_Id = ? ,[E-Mail] = ?, Phone = ?, Career_Id = ?, School_Year_Id = ? WHERE Code = ?", (name, carnet,genero,correo, telefono, carrera, año, codigo_update))
         cursor.commit()
         cursor.close()
         print(codigo_update)
         flash("Changes were made Satisfactorily")
         return redirect("/Alumnos")
      
   else:
      return redirect("/Alumnos")


@app.route('/RegistroDocentes', methods=["GET", "POST"])
def docentes():
   cursor = db.cursor()
   #Obtiene el ultimo Id Registrado y le suma una 
   comprobar_code = "SELECT MAX(Id) FROM Teachers"
   code_id = cursor.execute(comprobar_code).fetchone()[0]
   print(code_id)

   code = 0
   if(code_id is None):
      code = 1
      codigo = f"TEACHR0001"
   else:
      code = code_id+1
   print(code)

   #DOCENT0001    
   if code < 10:
      codigo = f"TEACHR000{code}"
   elif code < 100:
   #DOCENT099
      codigo = f"TEACHR00{code}"
   #DOCENT0999
   elif code < 1000:
      codigo = f"TEACHR0{code}"    
   else:
      codigo = f"TEACHR{code}" 


   if request.method == "POST":

      nombre = request.form.get("Nombre")
      correo = request.form.get("Correo")
      telefono = request.form.get("Telefono")
      dtp_id = request.form.get("Departamento")
      genero = request.form.get("Genero")
      codigo_upd = request.form['Codigo']

      #Se crea la imagen de Codigo QR
      qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
      #El nombre a poner
      qr.add_data(codigo)
      #Se genera el nuevo estilo del codigo QR
      img_QR = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
         
      #QR = Image.open(f"{carnet}"+".png")
      ruta = f"static/img/QR/{codigo}.png"
      img_QR.save(ruta)
      
      verificar = cursor.execute("SELECT *FROM Teachers WHERE Code = ?", (codigo_upd)).fetchone()
      if verificar is None:
         #Se envia a Firebase Storage 
         Send_QR(f"{codigo}",ruta)
         #Se obtiene el enlace para poder visualizar la imagen
         img = Link_Img(f"{codigo}")

         cursor.execute("INSERT INTO Teachers (NameTeacher,Gender_Id,[E-Mail],Phone,QR_img,Departament_Id) VALUES(?,?,?,?,?,?)",
                        (nombre,genero,correo,telefono,img,dtp_id))
         cursor.commit()
         cursor.close()
         remove(ruta)
         flash("Record added successfully")
         return redirect("/MasRegistros")
      else: 
         cursor.execute("UPDATE Teachers SET NameTeacher = ? ,Gender_Id = ?,[E-Mail] = ?, Phone = ?, Departament_Id = ? WHERE Code = ?",
                        (nombre,genero,correo,telefono,dtp_id,codigo_upd))
         cursor.commit()
         cursor.close()
         flash("Teacher modified successfullyy") 
         return redirect("/Docentes")       
   else:  
      return redirect("/Docentes")

@app.route('/RegistroClases', methods=["GET", "POST"])
def maestros():
   cursor = db.cursor() 
   #Variables
   nombre = request.form.get("Nombre")
   carrera_id = request.form.get("Carrera_Id")
   año_id = request.form.get("Año")
   codigo_upd = request.form.get("Codigo")

   if request.method=="POST":
      verificar = cursor.execute("SELECT NameClasse FROM Classes WHERE Code = ?",(codigo_upd)).fetchone()
      print(verificar)
      
      if verificar is None:
         cursor.execute("INSERT INTO Classes (NameClasse,Career_Id,School_Year_Id) VALUES(?,?,?)", (nombre,carrera_id,año_id))
         cursor.commit()
         cursor.close()
         flash("Record added successfully")
         return redirect("/Clases")
      else:
         cursor.execute("UPDATE Classes SET NameClasse = ? , Career_Id = ? , School_Year_Id =? WHERE Code = ?",(nombre,carrera_id,año_id,codigo_upd))
         cursor.commit()
         cursor.close()
         flash("Class modified successfully") 
         return redirect("/Clases")

   return redirect("/Clases")
#######################################################################

@app.route('/Horario',methods=['GET','POST'])
def hrario():
   cursor = db.cursor()
   query = "SELECT Id, NameCareer FROM Career"
   rows = cursor.execute(query).fetchall()

   Año = "SELECT Id,SchoolYearName FROM School_Year"
   row = cursor.execute(Año).fetchall()
   
   if request.method == "POST":
      carrera = request.form.get("Carrera")
      #print(carrera)
      an = request.form.get("Año")
      verificar = cursor.execute("SELECT a.Teacher_Id FROM Assignment a INNER JOIN Classes c ON a.Classes_Id = c.Id WHERE c.Career_Id = ? AND c.School_Year_Id = ? ",
      (carrera, an)).fetchone()
      if verificar is not None:
         flash("Horario encontrado")
         query = cursor.execute("EXEC usp_ViewHorario ?,?",(carrera,an)).fetchall()
         # Ordenar la tupla por el día de la semana
         horario = sorted(query, key=lambda x: x[7])
         #print(horario)
         return render_template("horario.html", hr = horario, carreras = rows , año = row)
      else:
         flash("No hay ningun horario aun")
      return render_template("horario.html",hr = "",carreras = rows , año = row)
   else:
      flash("Seleccione su carrera y Año para mostrar el horario")
   return render_template("horario.html",hr ="",carreras = rows , año = row)

@app.route('/MasRegistros', methods=["GET", "POST"])
def regisma():
   cursor = db.cursor()
   de = cursor.execute("SELECT Id, NameDepartament FROM Departament").fetchall()

   return render_template("uwu.html" , dep = de)

@app.route("/RegistroAsignaciones",methods=["GET", "POST"])
def asign():
   cursor = db.cursor()
   docent = cursor.execute("SELECT Id ,NameTeacher FROM Teachers").fetchall()
   clase = cursor.execute("SELECT Id, NameClasse FROM Classes").fetchall()
   dia = cursor.execute("SELECT Id, NameDay FROM Days").fetchall()
   lugar = cursor.execute("SELECT Id, Nameplace FROM Place").fetchall()
      
   view = cursor.execute("EXEC usp_ViewAsignaciones").fetchall()

   if request.method == "POST":
      hora_ini = request.form.get("HoraInicio")
      hora_fin = request.form.get("HoraFinal")
      dia_Id = request.form.get("Dia_Id")
      lugar_id = request.form.get("Lugar_Id")
      clase_Id =request.form.get("Clase_Id")
      docent_id = request.form.get("Maestros")

      verificar_Horario = cursor.execute("SELECT Id FROM School_Hours WHERE Class_Id = ?",(clase_Id)).fetchone()
      if verificar_Horario is None:
         cursor.execute("INSERT INTO School_Hours (StartTime,EndTime,Day_Id,Place_Id,Class_Id) VALUES(?,?,?,?,?)",
                        (hora_ini,hora_fin,dia_Id,lugar_id,clase_Id)) 
         cursor.execute("INSERT INTO Assignment (Teacher_Id, Classes_Id) VALUES(?,?)",(docent_id,clase_Id)) 
         cursor.commit()
         cursor.close()
         flash("Assignement Succesful")
         return redirect("/Asignaciones")
      else:
         cursor.execute("EXEC usp_Updt_Asignaciones ?,?,?,?,?,?",(hora_ini,hora_fin,clase_Id,docent_id,lugar_id,dia_Id))
         db.commit()
         cursor.close()
         flash("Modificado con exito")       
         return redirect("/Asignaciones")
   else:   
      return redirect("/Asignaciones")

@app.route('/AgregarUbicaciones', methods=["GET", "POST"])
def regisubi():
   cursor = db.cursor()
   if request.method == "POST":
      lugar = request.form.get("Lugar")
      verificar = cursor.execute("SELECT NamePlace FROM Place WHERE NamePlace = ?", (lugar)).fetchone()
      if verificar is None:
         cursor.execute("INSERT INTO Place (NamePlace) VALUES(?)",(lugar))
         cursor.commit()
         flash("Ubicacion Registrada")
         return render_template("uwu.html")
      else:
         flash("La ubicacion ya existe")  
         return render_template("uwu.html")

@app.route('/AgregarCarrera', methods=["GET", "POST"])
def asistencia():
   cursor = db.cursor()
   carrera = request.form.get("Carrera")
   dep = request.form.get("Departamento")
   if request.methods == "POST":
      
      de = cursor.execute("SELECT Id, NameDepartament FROM Departament").fetchall()

      verificar = cursor.execute("SELECT NameCareer FROM Career WHERE NameCaeer = ?", (carrera)).fetchone()
      if verificar is None:
         cursor.execute("INSERT INTO Career (NameCareer,Departament_Id) VALUES(?,?)",(carrera,dep))
         cursor.commit()
         flash("Registro Exitoso")
         cursor.close()
         return render_template("uwu.html", dep = de)
      else:
         flash("Registro Modificado con Exito")   
         return render_template("uwu.html", dep = de)


@app.route('/Asistencia', methods=['GET','POST'])
def asis():
   cursor = db.cursor()
   #variables obtenidas de Ajax
   clase = request.args.get("clase")
   codigo = request.args.get("Codigo")
   #Fecha actual
   fecha_actual = datetime.date.today()
      
   #Comprobando informacion
   #print(fecha_actual)
   #print(codigo)
   #print(clase)
   
   #Verifica si hay una clase en curso
   if clase is None:
      return render_template("qrscan.html", xd = "Nada", esta = "")  
   else:
      #esta = cursor.execute("EXEC usp_Estatistica ?,?",(str(clase), str(fecha_actual))).fetchall()
      Asistencia(fecha_actual,codigo,clase)
      xd = MostrarAsistenciaActual(clase,fecha_actual)
      cursor.close()                 
      #Se cierra la conexion 
      flash("Registro de Asistencia Exitoso")
      return render_template("qrscan.html", xd = xd, esta = 5)


#Region de Views o para Mostrar los Registros xd
@app.route('/Alumnos', methods=["GET", "POST"])
def viewA():
   cursor = db.cursor()

   query = "SELECT Id, NameCareer FROM Career"
   rows = cursor.execute(query).fetchall()

   Año = "SELECT Id,SchoolYearName FROM School_Year"
   row = cursor.execute(Año).fetchall()
   genero = cursor.execute("SELECT Id, NameGender FROM Gender").fetchall()

   #Procedimiento almacenado que muestra informacion de estudiantes
   consulta = cursor.execute("EXEC usp_ViewStudent").fetchall()
   print(consulta)
   
   #Verifica si existe o no
   if len(consulta) == 0:
      flash("Aun no hay nada aqui xd")
      return render_template("alumnos.html", Info = consulta,carreras = rows ,generos = genero ,Años = row)

   else:
      cursor.close()
      return render_template("alumnos.html", Info = consulta, carreras = rows ,generos = genero ,Años = row)
   
#Este hay que hacerlo desde 0 , con todo y diseño unu
@app.route('/Clases',methods=["GET", "POST"])
def viewClass():
   cursor = db.cursor()
   query = "SELECT Id, NameCareer FROM Career"
   rows = cursor.execute(query).fetchall()

   Año = "SELECT Id,SchoolYearName FROM School_Year"
   row = cursor.execute(Año).fetchall()

   consulta = cursor.execute("EXEC usp_ViewMateria").fetchall()

   #Verificar si hay registros 
   if len(consulta) == 0:
      flash("Aun no hay registros aqui")
      return render_template("materias.html", clases = consulta, carreras = rows , años = row)

   else:
      cursor.close()   
      return render_template("materias.html", clases = consulta, carreras = rows , años = row)



@app.route('/Docentes',methods=["GET", "POST"])
def viewDocen():
   cursor = db.cursor()
   
   dep = cursor.execute("SELECT Id, NameDepartament FROM Departament").fetchall()
   genero = cursor.execute("SELECT Id, NameGender FROM Gender").fetchall()
   consulta = cursor.execute("EXEC usp_ViewDocent").fetchall()
   

   if len(consulta) == 0:
      flash("Aun no hay registros Aqui")
      return render_template("maestros.html",Info = consulta, dep = dep, generos = genero)

   else:
      cursor.close()  
      return render_template("maestros.html",Info=consulta, dep=dep, generos=genero)
      

@app.route('/Asignaciones', methods=["GET","POST"])
def asignacion():
   cursor = db.cursor()
   docent = cursor.execute("SELECT Id ,NameTeacher FROM Teachers").fetchall()
   clase = cursor.execute("SELECT Id, NameClasse FROM Classes").fetchall()
   dia = cursor.execute("SELECT Id, NameDay FROM Days").fetchall()
   lugar = cursor.execute("SELECT Id, Nameplace FROM Place").fetchall()
   view = cursor.execute("EXEC usp_ViewAsignaciones").fetchall()
   
   if len(view) == 0:
      flash("Aun no hay asignaciones")
      return render_template("Asignaciones.html",xd = view,edit ="XD" ,maestros = docent, dias = dia, lugares = lugar, clases = clase)
   else:
      cursor.close()
      return render_template("Asignaciones.html",xd = view,edit="XD", maestros = docent, dias = dia, lugares = lugar, clases = clase)

#Editar Registros
@app.route('/EditarAlumno/<string:codigo>',methods=["GET", "POST"])
def rellenoAlumn(codigo):
   cursor = db.cursor()
   query = "SELECT Id, NameCareer FROM Career"
   rows = cursor.execute(query).fetchall()

   Año = "SELECT *FROM School_Year"
   row = cursor.execute(Año).fetchall()
   genero = cursor.execute("SELECT Id, NameGender FROM Gender").fetchall()

   query = cursor.execute("SELECT *FROM Students WHERE Code = ?",(codigo)).fetchone()
   cursor.close()
   return render_template("alumnos.html",title = "Edit Student", edit = query, carreras = rows , Años = row, generos = genero)


@app.route('/EditarDocente/<string:codigo>', methods=["GET","POST"])
def rellenoDocent(codigo):
   cursor = db.cursor()
   dep = cursor.execute("SELECT Id , NameDepartament FROM Departament").fetchall()
   genero = cursor.execute("SELECT Id, NameGender FROM Gender").fetchall()
   docent = cursor.execute("SELECT *FROM Teachers WHERE Code = ?",(codigo)).fetchone()
   cursor.close()
   return render_template("maestros.html",edit = docent, dep = dep, generos = genero)

#Hay que hacerlo de 0
@app.route('/EditarClase/<string:codigo>', methods = ["GET","POST"])
def rellenoclase(codigo):
   cursor = db.cursor()
   carrera = cursor.execute("SELECT *FROM Career").fetchall()
   Año = cursor.execute("SELECT *FROM School_Year").fetchall()
   clase = cursor.execute("SELECT *FROM Classes WHERE Code = ?",(codigo)).fetchone()
   cursor.close()
   return render_template("materias.html", edit = clase, carreras = carrera, años = Año)

@app.route('/EditarCarrera/<int:id>', methods=["GET","POST"])
def rellenocarrera(id):
   cursor = db.cursor()
   dep = "SELECT Id, NombreDepartament FROM Departament"
   row = cursor.execute(dep).fetchall()
   
   query = cursor.execute("SELECT *FROM Career WHERE Id = ? ", (id)).fetchone()
   return render_template("masregistros.html", edit = query , dept = row)

@app.route('/EditarUbicacion/<int:id>', methods=["GET","POST"])
def rellenoubi(id):
   cursor = db.cursor()
   xd = "SELECT *FROM Place WHERE Id = ?",(id)
   query = cursor.execute(xd).fetchone()
   cursor.close()
   return render_template("masregistros.html",edit2 = query)

@app.route('/EditarAsignacion/<string:codigo>',methods= ["GET","POST"])
def rellenoAsig(codigo):
   cursor = db.cursor()
   docent = cursor.execute("SELECT Id ,NameTeacher FROM Teachers").fetchall()
   clase = cursor.execute("SELECT Id, NameClasse FROM Classes").fetchall()
   dia = cursor.execute("SELECT Id, NameDay FROM Days").fetchall()
   lugar = cursor.execute("SELECT Id, Nameplace FROM Place").fetchall()
   view = cursor.execute("EXEC usp_ViewAsignaciones").fetchall()
   
   consult = cursor.execute("SELECT *FROM School_Hours s INNER JOIN Assignment a ON a.Classes_Id = s.Class_Id WHERE s.Code = ?",(codigo)).fetchone()
   return render_template("Asignaciones.html",xd = view ,edit = consult,clases = clase, maestros = docent, lugares = lugar, dias = dia)

@app.route('/EditarAsistencia/<int:id>', methods=["GET","POST"])
def rellenoAsis(id):
   cursor = db.cursor()

   a = "SELECT Id, NameStudent FROM Students"
   alum = cursor.execute(a).fetchall()
   xd = "SELECT Id, NameClass FROM Classess"
   clas = cursor.execute(xd).fetchall()

   query = cursor.execute("SELECT *FROM  Attendance WHERE Id = ?",(id)).fetchone()
   return render_template("masregistros.html", edit3 = query , alum = alum, clase = clas)


#Eliminar Registros
@app.route('/EliminarAlumno/<string:codigo>')
def deleteStu(codigo):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Students WHERE Code = ?", (codigo))
   cursor.commit()
   flash("Registro eliminado")
   cursor.close()
   return redirect("/Alumnos")

@app.route('/EliminarDocente/<string:codigo>')
def deletedocent(codigo):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Teachers WHERE Code = ?", (codigo))
   cursor.commit()
   flash("Registro eliminado")
   cursor.close()
   return redirect('/Docentes')

#Hay que hacerlo de 0
@app.route('/EliminarClase/<string:codigo>')
def deleteclas(codigo):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Classess WHERE Code = ?", (codigo))
   cursor.commit()
   cursor.close()
   flash("Registro eliminado")
   return redirect("/Clase")

@app.route('/EliminarAsistencia/<int:id>')
def deleteAsis(id):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Attendance WHERE id = ?", (id))
   cursor.commit()
   flash("Registro eliminado")
   return redirect("QrScanner.html")

@app.route('/EliminarCarrera/<int:id>')
def deletecar(id):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Career WHERE id = ?", (id))
   cursor.commit()
   flash("Registro eliminado")
   cursor.close()
   return redirect("RegMenores.html")

@app.route('/EliminarLugar/<int:id>')
def deletelugar(id):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Place WHERE id = ?", (id))
   cursor.commit()
   flash("Registro eliminado")
   cursor.close()
   redirect("/RegMenores")   

@app.route('/EliminarAsignacion/<int:id>')
def deleteasig(id):
   cursor = db.cursor()
   query = cursor.execute("DELETE FROM Assignment WHERE Id = ?",(id))
   query2 = cursor.execute("DELETE School_Hours WHERE Id=?",(id))
   cursor.commit()
   flash("Registro Eliminado")
   cursor.close()
   return redirect(url_for("RegMenores.html"))   


#Funcionalidades Propias XD

@app.route('/Search', methods=["GET", "POST"])
def search():
   cursor = db.cursor()
   if request.method=="POST":  
      dato = request.form.get("Search-Input")
      #print("Datoo:"+dato)
      query = cursor.execute("EXEC usp_Search ?", (dato)).fetchone()
      #print(len(query))
      #print(query)
      cursor.close()

      if query[0] == "707":
         flash("No hay ningun registro")
         return render_template("index.html")

      elif len(query) == 9:
      #print("Es Estudiante")
         return render_template("Alumnos.html", Info = query, query = 1)
      
      elif len(query) == 6:
      #print("Es Clase")
         return render_template("Materias.html", info = query, query = 1)
      
      elif len(query) == 10:
      #print("Es Docente") 
         return render_template("Maestros.html", Info = query, query = 1)
      else:  
         flash("No hay resultados")
         return render_template("index.html")
   else:
      flash("Es GET No POST :c")
      return render_template("index.html")  



@app.route('/Imagen/<codigo>', methods=["GET", "POST"])
def imagen(codigo):
   cursor = db.cursor()
   if request.method =="GET":
      Alumnos = cursor.execute("SELECT QR_Img FROM Students WHERE Code = ?",(codigo)).fetchone()

      if Alumnos is None:
         Docentes = cursor.execute("SELECT QR_Img FROM Teachers WHERE Code = ?", (codigo)).fetchone()
         url = Docentes[0]
         img = Link_Download(url)
         print(f"Es docente {Docentes}")
      else:   
         url = Alumnos[0]
         img = Link_Download(url)
         print(f"Es Alumno {Alumnos}")

      if Alumnos is None and Docentes is None:
         flash("No hay nada aqui")   

      #img = Link_Download("https://firebasestorage.googleapis.com/v0/b/project-qrimg.appspot.com/o/qr%2FESTUD0001?alt=media")
   return send_file(img, download_name=f"{codigo}.png")



#Region Login 
@app.route('/Login', methods=["GET", "POST"])
def login():
   cursor = db.cursor()
   if request.method == "POST":

      username = request.form.get("Username")
      password = request.form.get("Password")


      verificar = cursor.execute("SELECT *FROM Users WHERE username = ?", (username)).fetchone()
      if verificar is None:
         print("No existe el usuario")
         return render_template("Login.html")
      
      elif (check_password_hash(verificar[2],password)):
         session["user_id"] = verificar[0]
         user = session["username"] = verificar[1]
         flash(f"Welcome(a) {user}")
         return redirect("/")
      else:
         flash("Contraseña Incorrecta")
         return render_template("Login.html")
            
   return render_template("login.html")


@app.route('/RegistroUsuario', methods=["GET", "POST"])
def register():
      cursor = db.cursor()
      roles = cursor.execute("SELECT Id, Rolename FROM Roles").fetchall()
      #print(roles)

      if request.method == "POST":
         username = request.form.get("Username")
         password = request.form.get("Password")
         rol = request.form.get("Rol")
         confirm = request.form.get("Password-Confirm")

         hash = generate_password_hash(password)

         verificar = cursor.execute("SELECT *FROM Users WHERE username = ?",(username)).fetchone()

      if verificar is None:
         cursor.execute("INSERT INTO Users (Username, Password, Roles_Id) VALUES(?,?,?)",(username,hash,rol))
         cursor.commit()
         flash("Usuario Registrado Exitosamente")
         return render_template("Login.html", roles = roles)
      else:
         flash("Usuario Existente")   
         return render_template("Register.html", roles = roles)
      return render_template("Register.html" , roles = roles)


@app.route('/Logout', methods=["GET", "POST"])
def logout():
   session.clear() 
   flash("Usted ha Cerrado Session")
   return render_template("login.html")


if __name__ == "__main__":
   app.run(debug=True)
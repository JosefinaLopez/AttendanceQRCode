from io import BytesIO
#TODO Se usa django para la prueba de generar reportes , la idea es que se genere a partir de un template 
from django.http import  HttpResponse
from django.template.loader import get_template
#!Libreria encargada de convertir el template en un pdf 
from xhtml2pdf import  pisa

#? En el metodo, se manda el template html y si este se genera con datos de bd que se muestran con django
#? se usa lo segundo, para que en el pdf no solo se refleje el contenido html
def convert_to_pdf(template_src,morefromdjango={}):
    #!Se extrae el template
    template = get_template(template_src)
    #!Tambien la parte del django ,los datos
    html = template.render(morefromdjango)
    #!El resultado debe de estar en un formato para que se pueda convertir correctamente
    result = BytesIO()
    #!Se define el formato oficial 
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result)
    #!En caso de error , notifica
    if not pdf.err:
        return HttpResponse(result.getvalue(),conten_type = 'app/pdf')
    return None
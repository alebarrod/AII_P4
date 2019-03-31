from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh import qparser
import os

#Recibe una lista de correos y devuelve los nombres según el archivo agenda.txt
def getDestinyName(destinatarios):
    match = False
    nombres = list()

    agenda = open('Agenda\\agenda.txt', 'r')

    for persona in destinatarios:
        for line in agenda:
            if match:   #Cuando encuentra el nombre continua con el siguiente (deja de buscar coincidencias para ese)
                nombres.append(line)
                match = False
                break

            if line.find(persona) != -1:
                match = True
    return nombres

#Busquedas
##############################################
#Recibe una palabra y se busca en el cuerpo de los correos. Imprime los destinatarios y el cuerpo 
def busquedaCuerpo(busqueda, schema, ix):
    with ix.searcher() as searcher:
        query = QueryParser("cuerpo", ix.schema).parse(busqueda)
        resultados = searcher.search(query)
        for resultado in resultados:
            print("Destinatarios:\n" , resultado['nombreDestinatario'], "\nCuerpo:\n", resultado['cuerpo'])

#Recibe una palabra (nombre o apellido) y busca en los destinatarios. Imprime información con forme al apartado 'b'.
def buscaPorDestinatario(destinatario, schema, ix):
    with ix.searcher() as searcher:
        query = QueryParser("nombreDestinatario", ix.schema).parse(destinatario)
        resultados = searcher.search(query)
        for resultado in resultados:
            print("Destinatario: ", resultado["nombreDestinatario"], "\nRemitente: ", resultado["nombre"], "\nAsunto: ", resultado['asunto'], "\nFecha: ", resultado['fecha'])

#Recibe una lista de palabras y las busca en los asuntos de los correos. Imprime el nombre de los archivos de correo que los contienen (considerados spam).
def buscaPorFiltroSpam(palabras, schema, ix):
    filtro = ''
    for palabra in palabras:
        filtro = filtro + ' OR ' + palabra 
    filtro = filtro[4:]
    with ix.searcher() as searcher:
        query = QueryParser("asunto", ix.schema).parse(filtro)
        resultados = searcher.search(query)
        for resultado in resultados:
            print(resultado['fileName'])
##############################################

def createSchema():
    #Crea esquema whoosh
    schema = Schema(fileName = ID(stored = True), nombre = KEYWORD(stored = True), nombreDestinatario = KEYWORD(stored = True), asunto = KEYWORD(stored = True), cuerpo = TEXT(stored = True), fecha = ID(stored = True))
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    path = 'Correos'
    #Itetamos sobre los archivos contenidos en el directorio relativo 'Correos'
    files = os.listdir(path)
    for name in files:  #Por cada archivo
        correo = open('Correos\\'+str(name), 'r')


        #Extraemos la informacion del correo siguiendo el formato del ejercicio
        direccionOrigen = correo.readline()
        direccionOri = list()
        direccionOri.append(direccionOrigen)    #Introducirlo en lista para reutilizar el código de getDestinyName(...)
        nombre = getDestinyName(direccionOri)
        nombre = nombre[0].replace("\n", "")
        destino = correo.readline()
        destinatarios = destino.split(' ')
        nombres = getDestinyName(destinatarios)

        fecha = correo.readline()
        asunto = correo.readline()
        
        cuerpo = ''
        for line in correo.readlines():
            cuerpo += (line)
        correo.close()
        nombres = ' '.join(nombres)
        nombres = nombres.replace('\n','')
        
        #Anadimos el documento
        writer.add_document(fileName = name, nombre = nombre, nombreDestinatario = nombres, asunto = asunto, cuerpo = cuerpo, fecha = fecha)

    writer.commit() #Confirmar cambios

    return schema,ix

def main():

    schema,ix = createSchema()

    reponse = input("""Esquemas cargados. Elija el modo:
\na - Mostrar los remitentes y cuerpos de todos los correos que incluyan en el Cuerpo la
consulta de usuario (una palabra). Los remitentes se presentan con Nombre y Apellidos.
\nb - Mostrar todos los remitentes, destinatarios, asuntos y fechas de los correos que tengan
como algún destinatario el que introduzca el usuario. El usuario introduce el
destinatario a consultar con Nombre y Apellidos.
\nc - Se desea mostrar los nombres de los ficheros que contienen correos spam. Los correos
spam son aquellos que contienen en su Asunto alguna de las palabras que el usuario
introduce. Por ejemplo: 'Contrato Gracias compraventa'\n""")

    if reponse == 'a':
        busqueda = input("\nIntroduzca la palabra que desea buscar en el correo\n")
        busquedaCuerpo(busqueda, schema, ix)

    elif reponse == 'b':
        busqueda = input("\nIntroduzca nombre o apellidos\n")
        buscaPorDestinatario(busqueda, schema, ix)

    elif reponse == 'c':
        palabra = ""
        spamFilter = list()

        palabra = input("\nIntroduce palabras para el filtro de spam. Cuando termines pulsa enter.\n")
        spamFilter.append(palabra.replace("\n", ""))

        while palabra != "":
            palabra = input()
            spamFilter.append(palabra.replace("\n", ""))

        buscaPorFiltroSpam(spamFilter, schema, ix)

    else:
        input("\nError, intentelo de nuevo")
        exit()


#---------------------------------------------

main()
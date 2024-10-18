#!/usr/bin/env python


"""
Modulo que contiene funciones para trabajar con imagenes. En desarrollo.
Si se desea probar las funciones, acordarse de que las rutas en las cadenas
de texto deben de contener \\, por ejemplo: C:\\Users\\Usuario\\Desktop 
Tambien sirve utilizar la r: r"C:/Users/Usuario/Desktop" (se pueden poner
las barras invertidas, dependiendo de si tu sistema es Windows o Linux,
tener en cuenta que en los comentarios no se puede poner la barra \ junto
a un caracter),
"""

from PIL import Image
import os
import shutil
from datetime import datetime
import numpy as np
import cv2
#Librerias para pdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
#Librerias para SVG
import aspose.words as aw
#Libreria para borrar el fondo de una imagen
from rembg import remove

__author__ = "Adrian Mateos"
__copyright__ = "Copyright 2023"
__credits__ = []
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = ""
__email__ = "https://github.com/moraloamg"
__status__ = "Development"


def _imgvld(ruta:str):
    """
    Función que comprueba si un archivo es una imagen válida y sin corromper.

    Parameters:
    ----------
    - ruta (str): ruta de la imagen.

    Returns:
    --------
    - (bool): True si es una imagen, False si no lo es o es una imagen corrupta.
    """
    try:
        with Image.open(ruta) as img:
            img.verify()  # Verifica que el archivo sea una imagen válida
        return True
    except (IOError, SyntaxError) as e:
        return False


def _poner_indice_imagenes(activacion:bool, nombre:str, indice:int)->str:
    """
    Función que anade un indice a un archivo, ambos enviados por parámetro
    en caso de que la activacion sea True, por ejemplo; imagen_Nº_3
    Esta función está disenada para usarse dentro de otras funciones

    Parameters:
    ----------
    - activacion (bool): valor booleano que indica si se quiere o no poner un indice.
    - nombre (str): nombre del archivo.
    - indice (int): indice que se va a anadir al nombre del archivo

    Returns:
    --------
    - nombre_archivo (str): nombre final del archivo
    """

    #Si queremos que el nombre del archivo tenga un numero a modo de indice, extraemos el nombre y lo ponemos con el
    #contador (numero que ya viene dado en el nombre) junto con los caracteres "Nº", de esta manera tendremos las imagenes ordenadas
    #de lo contrario solo obtenemos el nombre del archivo.
    nombre_archivo = ""

    if activacion:
        #Separo por el '.' y me quedo con el elemento 0, es decir, el nombre, y se concateno el _Nº_ mas el indice
        nombre_archivo = f'{nombre.split(".")[0]}{"_Nº_"}{indice}'
    else:
        nombre_archivo = nombre.split(".")[0]

    return nombre_archivo


def _comprobar_duplicadas(ruta_directorio:str, nombre_archivo:str)->str:
    """
    Función que comprueba si un archivo se llama igual que otro y lo
    renombra con la fecha, hora, segundos y milisegundos actuales en caso de que esté
    duplicado, si no lo está se mantiene el nombre original.
    Esta función está disenada para usarse dentro de otras funciones

    Parameters:
    ----------
    - ruta_directorio (str): Ruta del directorio que contiene las imágenes.
    - nombre_archivo (str): nombre del archivo que se va a comprobar

    Returns:
    --------
    - nuevo_nombre (str): nuevo nombre que se crea, si no hay duplicados
    no se modifica, si hay duplicados se modifica.
    """

    nuevo_nombre = nombre_archivo
    
    #Si ya existe un archivo asi, nos metemos en el bucle
    if os.path.exists(os.path.join(ruta_directorio, nuevo_nombre)):
        #separamos la extension del nombre
        nombre, extension = os.path.splitext(nombre_archivo)

        # Agno/Mes/Día Hora:Minuto:Segundo:Milisegundo
        formato = "%Y-%m-%d_%H-%M-%S-%f"
        #nuevo nombre es igual al nombre original, mas _copia_ mas la fecha actual con el formato especificado,
        #recortando a tres milisegundos y mas la extension.
        nuevo_nombre = f"{nombre}{'_copia_'}{datetime.now().strftime(formato)}{extension}"

      
    return nuevo_nombre



def _contar_imagenes_en_directorio(directorio:str)->int:
    """
    Función que cuenta las imágenes que hay en un directorio.
    Esta función está disenada para usarse dentro de otras funciones

    Parameters:
    ----------
    - directorio (str): Ruta del directorio que contiene las imágenes.

    Returns:
    --------
    - contador (int): Número entero que indica la cantidad de imágenes.
    """

    contador = 0

    #Comprobamos que la ruta conduce a un directorio y que existe
    if os.path.exists(directorio) and os.path.isdir(directorio):
        #Iteramos los elementos del directorio
        for archivo in os.listdir(directorio):
            #Creamos la direccion completa
            ruta_archivo = os.path.join(directorio, archivo)
            #Nos aseguramos bien de que el archivo sea una imagen, integra y sin corromper (tambien si es SVG)
            if os.path.isfile(ruta_archivo) and _imgvld(ruta_archivo) or os.path.isfile(ruta_archivo) and ruta_archivo.lower().endswith('.svg'):
                contador += 1
    
    return contador
    
    
def _preparar_directorio(ruta: str, nombre:str)->str:
    """
    Función mediante la cual se crea el directorio que guardará archivos. Esta función no se puede
    usar por si sóla, sino dentro de otra función, como es el caso de 'redimensionar'.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que va a contener los archivos.
    - nombre (str): nombre del directorio.

    Returns:
    --------
    - nueva_ruta (str) ruta con el directorio que estará dentro de la carpeta origen que hayamos indicado.
    En caso de fallo, retornará None más un mensaje de error
    """
    #Creamos la nueva ruta con la actual mas el directorio que vamos a crear
    nueva_ruta = os.path.join(ruta, nombre)

    #En caso de que exista, preguntaremos al usuario si quiere remover el directorio con todo lo que haya dentro,
    #si no existe, crearemos el directorio
    if os.path.exists(nueva_ruta):
        # Pregunta al usuario si desea eliminar los directorios anidados
        respuesta = input(f"El directorio '{nueva_ruta}' ya existe. ¿Deseas borrarlo y su contenido? Si no lo elimina se cancelará la operación (s/n): ") #TODO esto se podria cambiar cuando no haya entrada de teclado
        
        if respuesta.lower() == 's':
            try:
                shutil.rmtree(nueva_ruta)
            except Exception as e:
                print(f'Error al eliminar directorio existente: {e}')
                return None
        else:
            print('Operación cancelada.')
            return None

    #creamos el directorio
    try:
        os.makedirs(nueva_ruta)
        return nueva_ruta
    except Exception as e:
        print(f'Error al crear el nuevo directorio: {e}')
        return None
    

def redimensionar_foto(ruta_origen:str, ruta_destino:str, ancho:int, alto:int=None, nombre:str=None, aviso:bool=True)->bool:
    """
    Función que redimensiona una imagen.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen redimensionada.
    - ancho (int): ancho de la imagen.
    - alto (int): alto de la imagen, None o vacio por defecto, no es necesario indicar éste parametro si se pretende
      hacer un reescalado simétrico de la imagen.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.


    Returns:
    --------
    - (bool) True en caso de exito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            with Image.open(ruta_origen) as imagen:

                #Comprobamos que existe la ruta que guarda las imagenes
                if os.path.isdir(ruta_destino):

                    #En caso de que el alto no se disponga por parametro, la imagen se reescalara con proporcion simetrica,
                    #en caso contrario, el reescalado obedecera a los parametros indicados por el usuario 
                    if alto != None:
                        nueva_imagen = imagen.resize((ancho,alto))
                    else:
                        ancho_original, alto_original = imagen.size
                        proporcion = ancho / ancho_original
                        alto_automatico = int(alto_original * proporcion)
                        nueva_imagen = imagen.resize((ancho, alto_automatico))

                    #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                    if nombre == None:
                        nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                    

                    #Extraemos y anadimos la extension original a la nueva foto
                    extension_original = os.path.splitext(ruta_origen)[1]
                    nombre = f"{nombre}{extension_original}"

                    #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                    #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                    nombre = _comprobar_duplicadas(ruta_destino, nombre)

                    #Convertir al modo RGB si es RGBA, es decir, si tiene canal Alpha y hay transparencia,
                    #ya que el formato JPEG o JPG no puede guardar datos en modo RGBA, por ende, quitamos la transparencia
                    #Guardamos la imagen en la nueva ruta y aumentamos el contador, utilizamos os.path.join para evitar
                    #problemas con la barra '\'
                    nueva_imagen.convert('RGB').save(os.path.join(ruta_destino, nombre))
                    return True
                else:
                    if aviso:
                        print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                    return False 

        except Exception as e:
            print(f'Ha ocurrido un error al redimensionar la imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False
    

def transformar_extension_imagen(ruta_origen:str, ruta_destino:str, extension:str, nombre:str=None ,aviso:bool=True)->bool:
    """
    Función que transforma la extension de una imagen. Las extensiones validas son: 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tif', 'tiff'.
    Al introducir la extension por parámetro NO se debe de incluir el punto delante de la extension.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen con la extension cambiada.
    - extension (str): extension de la imagen, sólo son validos los siguiente valores: 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tif', 'tiff'.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. nombre 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.


    Returns:
    --------
    - (bool) True en caso de éxito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #ponemos la extension en minusculas
    extension = extension.lower()

    EXTENSIONES_ADMITIDAS = ["jpg", "jpeg", "png", "bmp", "gif", "tif", "tiff"]

    #Comprobamos que la extension puesta por parametros esta entre las permitidas, en caso contrario, salimos
    if extension in EXTENSIONES_ADMITIDAS:

        #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
        if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
            try:
                with Image.open(ruta_origen) as imagen:

                    #Comprobamos que existe la ruta que guarda las imagenes
                    if os.path.isdir(ruta_destino):
               
                        if nombre == None:
                            #En caso de que no hayamos dado ningun nombre, pondremos el que tenia originalmente,
                            #extrayendolo de la ruta origen
                            futuro_nombre = f"{os.path.splitext(os.path.basename(ruta_origen))[0]}{'.'}{extension}"
                            
                        else:
                            #creamos el futuro nombre con el que hemos introducido por parametro
                            futuro_nombre = f"{nombre}{'.'}{extension}"
                    

                        #si esta duplicado se cambia el nombre anadiendose la fecha como identificador unico.
                        #si no esta duplicado se deja igual
                        #el parametro nombre_archivo (futuro nombre) de la siguiente funcion ha de tener la extension para
                        #funcionar correctamente
                        nombre = _comprobar_duplicadas(ruta_destino, futuro_nombre)
                        #quitamos la extension y extraemos el nombre, ya que la extension la cambiaremos despues
                        nombre = os.path.splitext(nombre)[0]

                        #combinamos la ruta del directorio de destino con el nombre del archivo que hemos dado por parametro
                        ruta_destino = os.path.join(ruta_destino, nombre)
                    
                        # Guardar la imagen con la extension
                        imagen.convert("RGB").save(f"{ruta_destino}.{extension}") #TODO UTILIZAR OS.PATH.JOIN COMO EL RESTO????????
                        return True
                    else:
                        if aviso:
                            print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                        return False  
                
            except Exception as e:
                print(f'Ha ocurrido un error al cambiar la extension de la imagen: {e}')
                return False
        else:
            if aviso and not os.path.isdir(ruta_origen):
                print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
            return False
    else:
        print(f'La extension {extension} no es admitida, las extensiones validas son las siguientes: "jpg", "jpeg", "png", "bmp", "gif", "tif", ".tiff"')
        return False


def redimensionar_varias_fotos(ruta:str, ancho:int, alto:int=None, numeracion_auto=False, aviso_fallos=False):
    """
    Función la cual aplica un reescalado a las imágenes halladas en un directorio.
    El reescalado puede ser asimétrico, indicado el ancho y alto que queramos (siempre mayor que 5 píxeles), o 
    simétrico, sólamente indicando el ancho.
    Finalmente, las imágenes tratadas se dispondrán un directorio llamado 'img_redimensionadas_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - ancho (int): ancho de la imagen.
    - alto (int): alto de la imagen, None o vacio por defecto, no es necesario indicar éste parametro si se pretende
      hacer un reescalado simétrico de la imagen.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes tratadas, dentro del directorio con el nombre 'img_redimensionadas_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #Comprobamos que las medidas que se introducen son adecuadas
        if (type(ancho) == int and ancho > 5) and ((type(alto) == int and alto > 5) or alto is None):
            #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
            nueva_ruta = _preparar_directorio(ruta, "img_redimensionadas_py")

            #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
            if nueva_ruta != None:
                #contador que sirve para averiguar la cantidad de fotos que se han transformado
                cont = 1

                #iteramos los archivos para transformarlos
                for archivo in os.listdir(ruta):
                    #obtenemos la direccion completa de la imagen para poder tratarla
                    ruta_imagen = os.path.join(ruta, archivo)
                    
                    #creamos el nombre del archivo
                    nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)

                    if redimensionar_foto(ruta_imagen,nueva_ruta,ancho,alto,nombre=nombre_archivo,aviso=aviso_fallos):
                        cont += 1

                print(f'Proceso terminado, {str(cont-1)} imagenes redimensionadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')  
        else:
            print('Los parametros ancho y alto deben ser numeros enteros y ambos mayores que 5')
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')



def modificar_extensiones_imagenes(ruta:str, extension:str, numeracion_auto=False, aviso_fallos=False):
    """
    Función que cambia las extensiones de varias imagenes en un directorio. 
    Las extensiones validas son: 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tif', 'tiff'.
    Al introducir la extension por parámetro NO se debe de incluir el punto delante de la extension.
    Las imágenes tratadas se dispondrán un directorio llamado 'img_transformadas_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - extension (str): extension de la imagen, sólo son validos los siguiente valores: 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tif', 'tiff'.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes tratadas, dentro del directorio con el nombre 'img_transformadas_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
        nueva_ruta = _preparar_directorio(ruta,'img_transformadas_py')

        #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
        if nueva_ruta != None:
            #contador que sirve para averiguar la cantidad de fotos que se han transformado
            cont = 1

            #iteramos los archivos para transformarlos
            for archivo in os.listdir(ruta):
                #obtenemos la direccion completa de la imagen para poder tratarla
                ruta_imagen = os.path.join(ruta, archivo)

                #creamos el nombre del archivo
                nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)
                
                if transformar_extension_imagen(ruta_imagen,nueva_ruta,extension,nombre_archivo,aviso_fallos):
                    cont = cont + 1

            print(f'Proceso terminado, {str(cont-1)} imagenes modificadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')         
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')
    


def comprimir_imagen(ruta_origen:str, ruta_destino:str, calidad:int, nombre:str=None ,aviso:bool=True)->bool:
    """
    Función que comprime la calidad de una imagen. 

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen con la extension cambiada.
    - calidad (int): calidad de la imagen.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. nombre 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.


    Returns:
    --------
    - (bool) True en caso de éxito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)


    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            with Image.open(ruta_origen) as imagen:

                #Comprobamos que existe la ruta que guarda las imagenes
                if os.path.isdir(ruta_destino):
                     
                    #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                    if nombre == None:
                        nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                    
                    #Extraemos y anadimos la extension original a la nueva foto
                    extension_original = os.path.splitext(ruta_origen)[1]
                    nombre = f"{nombre}{extension_original}"

                    #si esta duplicado se cambia el nombre anadiendose la fecha como identificador unico.
                    #si no esta duplicado se deja igual
                    #el parametro nombre_archivo (nombre) de la siguiente funcion ha de tener la extension para
                    #funcionar correctamente
                    nombre = _comprobar_duplicadas(ruta_destino, nombre)
                  
                    #combinamos la ruta del directorio de destino con el nombre del archivo que hemos dado por parametro
                    ruta_destino = os.path.join(ruta_destino, nombre)
                
                    # Guardar la imagen con la calidad deseada y la extension original
                    imagen.convert("RGB").save(ruta_destino, extension_original, calidad)
                    return True
                else:
                    if aviso:
                        print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                    return False  
            
        except Exception as e:
            print(f'Ha ocurrido un error al comprimir imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False
    

def comprimir_varias_imagenes(ruta:str, calidad:int, numeracion_auto=False, aviso_fallos=False):
    """
    Función que comprime la calidad de varias imágenes halladas en un directorio. 
    Las imágenes tratadas se dispondrán un directorio llamado 'img_comprimidas_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - calidad (int): calidad de la imagen.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes comprimidas, dentro del directorio con el nombre 'img_comprimidas_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
        nueva_ruta = _preparar_directorio(ruta,'img_comprimidas_py')

        #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
        if nueva_ruta != None:
            #contador que sirve para averiguar la cantidad de fotos que se han transformado
            cont = 1

            #iteramos los archivos para transformarlos
            for archivo in os.listdir(ruta):
                #obtenemos la direccion completa de la imagen para poder tratarla
                ruta_imagen = os.path.join(ruta, archivo)

                #creamos el nombre del archivo
                nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)
                
                if comprimir_imagen(ruta_imagen,nueva_ruta,calidad,nombre_archivo,aviso_fallos):
                    cont = cont + 1

            print(f'Proceso terminado, {str(cont-1)} imagenes comprimidas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')         
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')


def anadir_marca_de_agua(ruta_origen:str, ruta_destino:str, ruta_marca_agua:str, dimensiones_marca:int, nombre:str=None, transparencia:int=65, aviso:bool=True)->bool:
    """
    Función que anade una marca de agua a una imagen. 

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen con la extension cambiada.
    - ruta_marca_agua (str): ruta de la marca de agua, la imagen tendrá que tener un fondo transparente un resultado óptimo
    - dimensiones_marca (int): Dimensiones de la marca de agua, el tamano adecuado tiene que estar entre 90 y 5.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen.
    - transparencia (int): 65 por defecto. Marca el índice de transparencia de la marca de agua. Ha de estar entre 100 y 1. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.


    Returns:
    --------
    - (bool) True en caso de éxito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)
    ruta_marca_agua = os.path.normpath(ruta_marca_agua)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
    
        #Comprobamos que existe la ruta de la marca de agua
        if os.path.isfile(ruta_marca_agua) and _imgvld(ruta_marca_agua):

            #Comprobamos que existe la ruta que guarda las imagenes
            if os.path.isdir(ruta_destino):

                #Comprobamos que las dimensiones de la marca de agua son las correctas
                if dimensiones_marca <=90 and dimensiones_marca > 5:

                    #Comprobamos que el indice de transparencia es adecuado  
                    if transparencia <=100 and transparencia >=1 :
                        try:  
                            with Image.open(ruta_origen) as imagen, Image.open(ruta_marca_agua) as marca_de_agua:

                                #Obtener las dimensiones de la imagen principal
                                ancho, alto = imagen.size

                                #Calcular las nuevas dimensiones de la marca de agua
                                ancho_marca = int(ancho * dimensiones_marca / 100)
                                ratio_aspecto = float(marca_de_agua.size[1]) / float(marca_de_agua.size[0])
                                alto_marca = int(ancho_marca * ratio_aspecto)

                                #Redimensionar la marca de agua manteniendo la proporción
                                marca_de_agua = marca_de_agua.resize((ancho_marca, alto_marca))

                                #obtenemos las coordenadas del centro de la imagen
                                x = (ancho - ancho_marca) // 2
                                y = (alto - alto_marca) // 2

                                #Crear una copia de la imagen principal para superponer la marca de agua
                                imagen_con_marca_de_agua = imagen.copy()

                                #Pegar la marca de agua en las coordenadas calculadas
                                imagen_con_marca_de_agua.paste(marca_de_agua, (x, y), marca_de_agua)

                                #Aplicar la transparencia de a la marca de agua
                                imagen_con_marca_de_agua = Image.blend(imagen, imagen_con_marca_de_agua, transparencia / 100)

                                #Convertir la imagen resultante al modo RGB antes de guardarla en formato JPEG
                                imagen_con_marca_de_agua = imagen_con_marca_de_agua.convert("RGB")
                                
                                #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                                if nombre == None:
                                    nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                                

                                #Extraemos y anadimos la extension original a la nueva foto
                                extension_original = os.path.splitext(ruta_origen)[1]
                                nombre = f"{nombre}{extension_original}"

                                #si esta duplicado se cambia el nombre anadiendose la fecha como identificador unico.
                                #si no esta duplicado se deja igual
                                #el parametro nombre_archivo (nombre) de la siguiente funcion ha de tener la extension para
                                #funcionar correctamente
                                nombre = _comprobar_duplicadas(ruta_destino, nombre)
                            
                                #combinamos la ruta del directorio de destino con el nombre del archivo que hemos dado por parametro
                                ruta_destino = os.path.join(ruta_destino, nombre)
                            
                                # Guardar la imagen con la marca de agua
                                imagen_con_marca_de_agua.save(ruta_destino)
                                return True
                        
                        except Exception as e:
                            if aviso:
                                print(f'Ha ocurrido el siguiente error al poner la marca de agua: {e}')
                            return False
                    else:
                        if aviso:
                            print(f'El indice de transparencia debe de ser menor a 100 y mayor a 1')
                        return False
                else:
                    if aviso:
                        print(f'Las dimensiones de la marca han de estar entre 90 y 5')
                    return False
            else:
                if aviso:
                    print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                return False   
        else:
            if aviso:
                print(f'La ruta {ruta_marca_agua} no corresponde a una foto o esta corrupta')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False


def marcar_agua_varias_imagenes(ruta:str, ruta_marca_agua:str, dimensiones_marca:int, transparencia_imagenes:int=65, numeracion_auto=False, aviso_fallos=False):
    """
    Función que anade marcas de agua a las imágenes de un directorio. 
    Las imágenes tratadas se dispondrán un directorio llamado 'img_marcadas_agua_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - ruta_marca_agua (str): ruta de la marca de agua, la imagen tendrá que tener un fondo transparente un resultado óptimo
    - dimensiones_marca (int): Dimensiones de la marca de agua, el tamano adecuado tiene que estar entre 90 y 5.
    - transparencia_imagenes (int): 65 por defecto. Marca el índice de transparencia de la marca de agua. Ha de estar entre 100 y 1.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes marcadas, dentro del directorio con el nombre 'img_marcadas_agua_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)
    ruta_marca_agua = os.path.normpath(ruta_marca_agua)

    #Comprobamos que las dimensiones de la marca de agua son las correctas
    if dimensiones_marca <=90 and dimensiones_marca > 5:

        #Comprobamos que el indice de transparencia es adecuado  
        if transparencia_imagenes <=100 and transparencia_imagenes >=1 :

            #comprobamos que existe la ruta y que es un directorio
            if os.path.exists(ruta) and os.path.isdir(ruta):

                #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
                nueva_ruta = _preparar_directorio(ruta,'img_marcadas_agua_py')

                #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
                if nueva_ruta != None:
                    #contador que sirve para averiguar la cantidad de fotos que se han transformado
                    cont = 1

                    #iteramos los archivos para transformarlos
                    for archivo in os.listdir(ruta):
                        #obtenemos la direccion completa de la imagen para poder tratarla
                        ruta_imagen = os.path.join(ruta, archivo)

                        #creamos el nombre del archivo
                        nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)
                        
                        #Ojo! cuidado con el orden de los parametros, aqui 'aviso' tiene que ser indicado con 'aviso_fallos'
                        if anadir_marca_de_agua(ruta_imagen, nueva_ruta, ruta_marca_agua, dimensiones_marca, nombre_archivo, transparencia=transparencia_imagenes, aviso=aviso_fallos):
                            cont = cont + 1

                    print(f'Proceso terminado, {str(cont-1)} imagenes marcadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')         
            else:
                print('El directorio introducido por parametro no existe o no es un directorio')
        else:
            print(f'El indice de transparencia debe de ser menor a 100 y mayor a 1')
    else:           
        print(f'Las dimensiones de la marca han de estar entre 90 y 5')



def rotar_imagen(ruta_origen:str, ruta_destino:str, grados:int, nombre:str=None, aviso:bool=True)->bool:
    """
    Función que rota una imagen en unos angulos permitidos.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen rotada.
    - grados (int): grados de la imagen, solo permitidos los valores de 90, -90, y 180.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - (bool) True en caso de exito, False en caso de fracaso más un mensaje de error.
    """

    ANGULOS_PERMITIDOS = [90, -90, 180, -180]

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            with Image.open(ruta_origen) as imagen:

                #Comprobamos que existe la ruta que guarda las imagenes
                if os.path.isdir(ruta_destino):

                    if grados in ANGULOS_PERMITIDOS:

                        #rotamos la imagen. Es necesario poner expand=True, ya que si no la imagen puede salir recortada
                        nueva_imagen = imagen.rotate(grados, expand=True)

                        #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                        if nombre == None:
                            nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                        
                        #Extraemos y anadimos la extension original a la nueva foto
                        extension_original = os.path.splitext(ruta_origen)[1]
                        nombre = f"{nombre}{extension_original}"

                        #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                        #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                        nombre = _comprobar_duplicadas(ruta_destino, nombre)

                        #Guardamos la nueva imagen
                        nueva_imagen.convert('RGB').save(os.path.join(ruta_destino, nombre))

                        return True
                    else:
                        if aviso:
                            print(f'El ángulo {grados}, no es válido, solo son válidos los ángulos 90, -90, y 180')
                        return False
                else:
                    if aviso:
                        print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                    return False 

        except Exception as e:
            print(f'Ha ocurrido un error al rotar la imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False


def rotar_varias_imagenes(ruta:str, grados:int, numeracion_auto=False, aviso_fallos=False):
    """
    Función que rota imágenes halladas en un directorio dado un angulo entre unos valores determinados. 
    Las imágenes tratadas se dispondrán un directorio llamado 'img_rotadas_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - grados (int): grados de la imagen, solo permitidos los valores de 90, -90, 180.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes rotadas, dentro del directorio con el nombre 'img_rotadas_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    ANGULOS_PERMITIDOS = [90, -90, 180]

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):
        if grados in ANGULOS_PERMITIDOS:

            #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
            nueva_ruta = _preparar_directorio(ruta,'img_rotadas_py')

            #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
            if nueva_ruta != None:
                #contador que sirve para averiguar la cantidad de fotos que se han transformado
                cont = 1

                #iteramos los archivos para transformarlos
                for archivo in os.listdir(ruta):
                    #obtenemos la direccion completa de la imagen para poder tratarla
                    ruta_imagen = os.path.join(ruta, archivo)

                    #creamos el nombre del archivo
                    nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)
                    
                    if rotar_imagen(ruta_imagen,nueva_ruta,grados,nombre_archivo,aviso_fallos):
                        cont = cont + 1

                print(f'Proceso terminado, {str(cont-1)} imagenes rotadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas') 
        else:      
            print(f'El ángulo {grados}, no es válido, solo son válidos los ángulos 90, -90 y 180')                
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')


def voltear_imagen(ruta_origen:str, ruta_destino:str, direccion:int, nombre:str=None, aviso:bool=True)->bool:
    """
    Función que inverte una imagen, de izquierda a derecha o arriba y abajo.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen rotada.
    - direccion (int): 1 para invertir de izquerda a derecha, 2 para invertir de arriba a abajo.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - (bool) True en caso de exito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            with Image.open(ruta_origen) as imagen:

                #Comprobamos que existe la ruta que guarda las imagenes
                if os.path.isdir(ruta_destino):

                    if direccion in [1,2]:
                        
                        #volteamos la imagen dependiento del parameto introducido
                        if direccion == 1:
                            #de izquierda a derecha
                            nueva_imagen = imagen.transpose(Image.FLIP_LEFT_RIGHT)
                        else:
                            #de arriba a abajo
                            nueva_imagen = imagen.transpose(Image.FLIP_TOP_BOTTOM)

                        #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                        if nombre == None:
                            nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                        
                        #Extraemos y anadimos la extension original a la nueva foto
                        extension_original = os.path.splitext(ruta_origen)[1]
                        nombre = f"{nombre}{extension_original}"

                        #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                        #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                        nombre = _comprobar_duplicadas(ruta_destino, nombre)

                        #Guardamos la nueva imagen
                        nueva_imagen.convert('RGB').save(os.path.join(ruta_destino, nombre))

                        return True
                    else:
                        if aviso:
                            print("El parametro direccion debe de ser 1, para volteo horizontal o 2, para volteo vertical")
                        return False
                else:
                    if aviso:
                        print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                    return False 

        except Exception as e:
            print(f'Ha ocurrido un error al voltear la imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False


def voltear_varias_imagenes(ruta:str, direccion:int, numeracion_auto=False, aviso_fallos=False):
    """
    Función que invierte imágenes halladas en un directorio, de izquierda a derecha o de arriba a abajo. 
    Las imágenes tratadas se dispondrán un directorio llamado 'img_invertidas_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - direccion (int): 1 para invertir de izquerda a derecha, 2 para invertir de arriba a abajo.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes invertidas, dentro del directorio con el nombre 'img_invertidas_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        if direccion in [1,2]:
            #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
            nueva_ruta = _preparar_directorio(ruta,'img_invertidas_py')

            #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
            if nueva_ruta != None:
                #contador que sirve para averiguar la cantidad de fotos que se han transformado
                cont = 1

                #iteramos los archivos para transformarlos
                for archivo in os.listdir(ruta):
                    #obtenemos la direccion completa de la imagen para poder tratarla
                    ruta_imagen = os.path.join(ruta, archivo)

                    #creamos el nombre del archivo
                    nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)
                    
                    if voltear_imagen(ruta_imagen,nueva_ruta,direccion,nombre_archivo,aviso_fallos):
                        cont = cont + 1

                print(f'Proceso terminado, {str(cont-1)} imagenes rotadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas') 
        else:      
            print("El parametro direccion debe de ser 1, para volteo horizontal o 2, para volteo vertical")                 
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')



def _algoritmo_cortar_bordes(imagen_con_bordes:Image):
    """
    Función que contiene un algoritmo para detectar y recortar bordes negros de una imagen.

    Parameters:
    ----------
    - image_con_bordes (PIL.Image): objeto de la clase PIL.Image, que contiene la imagen con bordes negros.

    Returns:
    --------
    - corte (numpy.array): matriz con los datos de la imagen que ha sido recortada.
    """
    
    #Convierte la imagen de entrada en una matriz NumPy.
    imagen_con_bordes = np.array(imagen_con_bordes)
    #Convierte la imagen a escala de grises utilizando la función `cvtColor` de OpenCV
    imagen_gris = cv2.cvtColor(imagen_con_bordes, cv2.COLOR_BGR2GRAY)
    #Aplica un umbral a la imagen en escala de grises para binarizarla, convirtiendo los píxeles en blanco o negro.
    #Los píxeles con intensidades menores que 1 se convierten en negro (0)
    #y los píxeles con intensidades mayores se convierten en blanco (255).
    _, sesgo = cv2.threshold(imagen_gris, 1, 255, cv2.THRESH_BINARY)
    #Encuentra los contornos de la imagen binarizada utilizando la función `findContours` de OpenCV. `RETR_EXTERNAL`
    #significa que solo se devolverán los contornos externos y `CHAIN_APPROX_SIMPLE` significa que se utilizará una
    #aproximación de contorno simple.
    contornos, _ = cv2.findContours(sesgo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #Inicializa variables para almacenar el contorno más grande encontrado y su área máxima.
    mas_grande = np.array([])
    area_max = 0
    #Itera sobre todos los contornos encontrados. Calcula el área de cada contorno, su perímetro
    #y una aproximación de polígono con la función `approxPolyDP` de OpenCV.
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        peri = cv2.arcLength(contorno, True)
        aprox = cv2.approxPolyDP(contorno, 0.02 * peri, True)
        #Si el área del contorno actual es mayor que la máxima área encontrada hasta ahora y la cantidad
        #de vértices de la aproximación del polígono es 4 (lo que indica que el contorno podría ser un cuadrilátero),
        #actualiza las variables `biggest` y `max_area` para almacenar este contorno.
        if area > area_max and len(aprox) == 4:
            mas_grande = aprox
            area_max = area
    #Encuentra el rectángulo delimitador del contorno más grande y recorta la imagen original utilizando este rectángulo delimitador.
    cnt = mas_grande
    x, y, w, h = cv2.boundingRect(cnt)
    corte = imagen_con_bordes[y : y + h, x : x + w]
    #Devuelve la imagen recortada que representa la región de interés sin los bordes negros.
    return corte





def recortar_bordes_negros(ruta_origen:str, ruta_destino:str, nombre:str=None, aviso:bool=True)->bool:
    """
    Función que recorta los bordes negros de una imagen.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen rotada.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - (bool) True en caso de exito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            with Image.open(ruta_origen) as imagen:

                #Comprobamos que existe la ruta que guarda las imagenes
                if os.path.isdir(ruta_destino):
                        
                        #el formato de salida es un numpy.ndarray, y hay que pasarlo a Image con .fromarray
                        nueva_imagen = Image.fromarray(_algoritmo_cortar_bordes(imagen))

                        #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                        if nombre == None:
                            nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                        
                        #Extraemos y anadimos la extension original a la nueva foto
                        extension_original = os.path.splitext(ruta_origen)[1]
                        nombre = f"{nombre}{extension_original}"

                        #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                        #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                        nombre = _comprobar_duplicadas(ruta_destino, nombre)

                        #Guardamos la nueva imagen
                        nueva_imagen.convert('RGB').save(os.path.join(ruta_destino, nombre))

                        return True
                    
                else:
                    if aviso:
                        print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                    return False 

        except Exception as e:
            print(f'Ha ocurrido un error al voltear la imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False



def recortar_varios_bordes_negros(ruta:str, numeracion_auto=False, aviso_fallos=False):
    """
    Función que elimina los bordes negros de fotos halladas en un directorio. 
    Las imágenes tratadas se dispondrán un directorio llamado 'img_sin_borde_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes con los bordes negros recortados, dentro del directorio con el nombre 'img_sin_borde_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
        nueva_ruta = _preparar_directorio(ruta,'img_sin_borde_py')

        #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
        if nueva_ruta != None:
            #contador que sirve para averiguar la cantidad de fotos que se han transformado
            cont = 1

            #iteramos los archivos para transformarlos
            for archivo in os.listdir(ruta):
                #obtenemos la direccion completa de la imagen para poder tratarla
                ruta_imagen = os.path.join(ruta, archivo)

                #creamos el nombre del archivo
                nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)

                if recortar_bordes_negros(ruta_imagen, nueva_ruta, nombre_archivo, aviso_fallos):
                    cont = cont + 1

            print(f'Proceso terminado, {str(cont-1)} imagenes recortadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')                
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')




def recortar_foto(ruta_origen:str, ruta_destino:str, margen_der:int=0, margen_izq:int=0, margen_sup:int=0, margen_inf:int=0, nombre:str=None, aviso:bool=True)->bool:
    """
    Función que recorta una imagen. Se toman como referencia los margenes de la foto y
    la distancia de recortado (en pixeles) se cuentan conforme a dichos margenes.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen recortada.
    - margen_der (int): margen derecha de la foto en pixeles, por defecto a 0 px.
    - margen_izq (int): margen izquierda de la foto en pixeles, por defecto a 0 px.
    - margen_sup (int): margen superior de la foto en pixeles, por defecto a 0 px.
    - margen_inf (int): margen inferior de la foto en pixeles, por defecto a 0 px.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.


    Returns:
    --------
    - (bool) True en caso de exito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            with Image.open(ruta_origen) as imagen:

                #Comprobamos que existe la ruta que guarda las imagenes
                if os.path.isdir(ruta_destino):

                    #obtenemos el alto y ancho de la imagen
                    ancho, alto = imagen.size
    
                    #definimos las coordenadas del area a recortar
                    izquierda = margen_izq
                    superior = margen_sup
                    derecha = ancho - margen_der
                    inferior = alto - margen_inf
                    
                    #recortamos las imagen
                    nueva_imagen = imagen.crop((izquierda, superior, derecha, inferior))

                    #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                    if nombre == None:
                        nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                    

                    #Extraemos y anadimos la extension original a la nueva foto
                    extension_original = os.path.splitext(ruta_origen)[1]
                    nombre = f"{nombre}{extension_original}"

                    #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                    #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                    nombre = _comprobar_duplicadas(ruta_destino, nombre)

                    #Convertir al modo RGB si es RGBA, es decir, si tiene canal Alpha y hay transparencia,
                    #ya que el formato JPEG o JPG no puede guardar datos en modo RGBA, por ende, quitamos la transparencia
                    #Guardamos la imagen en la nueva ruta y aumentamos el contador, utilizamos os.path.join para evitar
                    #problemas con la barra '\'
                    nueva_imagen.convert('RGB').save(os.path.join(ruta_destino, nombre))
                    return True
                else:
                    if aviso:
                        print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                    return False 

        except Exception as e:
            print(f'Ha ocurrido un error al recortar la imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False
    


def recortar_varias_fotos(ruta:str, margen_der:int=0, margen_izq:int=0, margen_sup:int=0, margen_inf:int=0, numeracion_auto=False, aviso_fallos=False):
    """
    Función la cual aplica un recorte a las imágenes halladas en un directorio.
    El recorte tomará como referencia los márgenes de las fotos. La medida será en pixeles.
    Las imágenes tratadas se dispondrán un directorio llamado 'img_recortadas_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - margen_der (int): margen derecha de la foto en pixeles, por defecto a 0 px.
    - margen_izq (int): margen izquierda de la foto en pixeles, por defecto a 0 px.
    - margen_sup (int): margen superior de la foto en pixeles, por defecto a 0 px.
    - margen_inf (int): margen inferior de la foto en pixeles, por defecto a 0 px.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes tratadas, dentro del directorio con el nombre 'img_recortadas_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #Comprobamos que las medidas que se introducen son adecuadas
        if (margen_der >= 0 and margen_izq >= 0 and margen_sup >= 0 and margen_inf >= 0):
            if (isinstance(margen_izq, int) and isinstance(margen_der, int) and isinstance(margen_sup, int) and isinstance(margen_inf, int)):

                #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
                nueva_ruta = _preparar_directorio(ruta, "img_recortadas_py")

                #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
                if nueva_ruta != None:
                    #contador que sirve para averiguar la cantidad de fotos que se han transformado
                    cont = 1

                    #iteramos los archivos para transformarlos
                    for archivo in os.listdir(ruta):
                        #obtenemos la direccion completa de la imagen para poder tratarla
                        ruta_imagen = os.path.join(ruta, archivo)
                        
                        #creamos el nombre del archivo
                        nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)

                        if recortar_foto(ruta_imagen,nueva_ruta,margen_der,margen_izq,margen_sup,margen_inf,nombre=nombre_archivo,aviso=aviso_fallos):
                            cont += 1

                    print(f'Proceso terminado, {str(cont-1)} imagenes recortadas de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')
            else:
                print('Los parametros deben de ser numeros enteros')
        else:
            print('Los parametros de los margenes debe de ser mayor o igual que cero')
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')

#-------------- TODO revisar un poco el codigo a partir de aqui-------------

def varias_fotos_a_pdf(ruta:str, nombre_archivo:str, aviso_fallos=False):
    """
    Función la cual combina en un pdf las imágenes halladas en un directorio.
    Las paginas del pdf tomaran el mismo orden que tengan estas en el directorio.
    Finalmente, las imágenes tratadas se dispondrán un directorio llamado 'pdf_imagenes_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - nombre_archivo (str): Nombre del archivo pdf.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - pdf con las imagenes, dentro del directorio con el nombre 'pdf_imagenes_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #obtenemos la nueva ruta donde guardaremos el pdf
        nueva_ruta = _preparar_directorio(ruta, "pdf_imagenes_py")

        #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
        if nueva_ruta != None:
            #contador que sirve para averiguar la cantidad de fotos que se han transformado
            cont = 1

            # Crear un objeto PDF
            nombre_pdf = os.path.join(nueva_ruta, nombre_archivo + '.pdf')
            pdf = canvas.Canvas(nombre_pdf, pagesize=letter)

            #iteramos los archivos para transformarlos
            for archivo in os.listdir(ruta):
                #obtenemos la direccion completa de la imagen para poder tratarla
                ruta_imagen = os.path.join(ruta, archivo)
                
                if ruta_imagen.endswith(".jpg") or ruta_imagen.endswith(".png"):
                    try:
                        # Cargar la imagen
                        img = Image.open(ruta_imagen)

                        # Obtener dimensiones de la imagen
                        ancho, alto = img.size

                        # Establecer el tamaño de la página según el tamaño de la imagen
                        pdf.setPageSize((ancho, alto))

                        # Dibujar la imagen en la página
                        pdf.drawImage(ruta_imagen, 0, 0, ancho, alto)
                        # Añadir la página al PDF
                        pdf.showPage()  

                        cont += 1
                    except Exception as e:
                        if aviso_fallos:
                            print(f"Error procesando {archivo}: {e}")
            
            #Guardamos el pdf con todos los datos y paginas creadas
            pdf.save()

            print(f'Proceso terminado, {str(cont-1)} imagenes insertadas en pdf de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')  
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')


def imagen_svg_a_png(ruta_origen:str, ruta_destino:str, nombre:str=None ,aviso:bool=True)->bool:
    """
    Función que transforma una imagen .svg a .png.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen SVG.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen transformada a PNG.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. nombre 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - (bool) True en caso de éxito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es un .svg
    if os.path.isfile(ruta_origen) and os.path.splitext(ruta_origen)[1].lower() == '.svg':
        try:
            #Comprobamos que existe la ruta que guarda las imagenes
            if os.path.isdir(ruta_destino):
                #En caso de que el alto no se disponga por parametro, la imagen se reescalara con proporcion simetrica,
                #en caso contrario, el reescalado obedecera a los parametros indicados por el usuario 

                #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                if nombre == None:
                    nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                

                #Extraemos y anadimos la nueva extension, en este caso .png, a la foto
                extension_nueva = ".png"
                nombre = f"{nombre}{extension_nueva}"

                #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                nombre = _comprobar_duplicadas(ruta_destino, nombre)

                #aqui se utiliza la libreria aspose.words
                #cargar el documento
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)

                #insertar la imagen SVG
                shape = builder.insert_image(ruta_origen)

                #crear opciones de guardado con mayor calidad
                options = aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)

                #establecer resoluciones horizontal y vertical (en DPI)
                options.horizontal_resolution = 300  # Resolución horizontal
                options.vertical_resolution = 300    # Resolución vertical

                #guardar la imagen
                shape.get_shape_renderer().save(os.path.join(ruta_destino, nombre), options)

                return True
            else:
                if aviso:
                    print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                return False  
            
        except Exception as e:
            print(f'Ha ocurrido un error al transformar a PNG el archivo SVG: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a un .svg o esta corrupta')
        return False
    

def imagenes_svg_a_png(ruta:str, numeracion_auto=False, aviso_fallos=False):
    """
    Función la cual convierte imagenes vectoriales SVG de un directorio en PNG
    Finalmente, las imágenes tratadas se dispondrán un directorio llamado 'img_PNG_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes tratadas, dentro del directorio con el nombre 'img_PNG_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
        nueva_ruta = _preparar_directorio(ruta, "img_PNG_py")

        #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
        if nueva_ruta != None:
            #contador que sirve para averiguar la cantidad de fotos que se han transformado
            cont = 1

            #iteramos los archivos para transformarlos
            for archivo in os.listdir(ruta):
                #obtenemos la direccion completa de la imagen para poder tratarla
                ruta_imagen = os.path.join(ruta, archivo)
                
                #creamos el nombre del archivo
                nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)

                if imagen_svg_a_png(ruta_imagen,nueva_ruta,nombre=nombre_archivo,aviso=aviso_fallos):
                    cont += 1

            print(f'Proceso terminado, {str(cont-1)} SVG tratados de {_contar_imagenes_en_directorio(ruta)} SVG encontrados')        
    else:
        print('El directorio introducido por parametro no existe o no es un directorio')


def borrar_fondo_foto(ruta_origen:str, ruta_destino:str, nombre:str=None, aviso:bool=True)->bool:
    """
    Función que borra el fondo de una imagen, muy útil para quitar el fondo blanco de un retrato.

    Parameters:
    ----------
    - ruta_origen (str): Ruta del directorio donde se encuentra la imagen.
    - ruta_destino (str): nombre del directorio de destino donde se guardara la imagen redimensionada.
    - nombre (str): None por defecto. Nombre (sin extension) en caso de que queramos renombrar la imagen. 
    - aviso (bool): True por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.


    Returns:
    --------
    - (bool) True en caso de exito, False en caso de fracaso más un mensaje de error.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta_origen = os.path.normpath(ruta_origen)
    ruta_destino = os.path.normpath(ruta_destino)

    #Comprobamos que existe la ruta y que el archivo es una imagen integra y sin corromper
    if os.path.isfile(ruta_origen) and _imgvld(ruta_origen):
        try:
            #Comprobamos que existe la ruta que guarda las imagenes
            if os.path.isdir(ruta_destino):

                with open(ruta_origen, "rb") as entrada_imagen:

                    #leemos la imagen
                    imagen = entrada_imagen.read()
                    imagen_sin_fondo = remove(imagen)
                    

                    #En caso de que no hayamos dado ningun nombre, podremos el que tenia
                    if nombre == None:
                        nombre = os.path.splitext(os.path.basename(ruta_origen))[0]
                    

                    #Extraemos y anadimos la extension original a la nueva foto
                    extension_original = os.path.splitext(ruta_origen)[1]
                    nombre = f"{nombre}{extension_original}"

                    #comprobamos que no existe una imagen llamada igual que la nueva, en caso contrario, la renombramos con la
                    #fecha actual. El parametro nombre ha de tener la extension para funcionar correctamente
                    nombre = _comprobar_duplicadas(ruta_destino, nombre)


                    #Convertir al modo RGB si es RGBA, es decir, si tiene canal Alpha y hay transparencia,
                    #ya que el formato JPEG o JPG no puede guardar datos en modo RGBA, por ende, quitamos la transparencia
                    #Guardamos la imagen en la nueva ruta y aumentamos el contador, utilizamos os.path.join para evitar
                    #problemas con la barra '\'

                    nombre_definitivo = os.path.join(ruta_destino, nombre)

                with open(nombre_definitivo, "wb") as salida_final:
                    salida_final.write(imagen_sin_fondo)

                    return True

            else:
                if aviso:
                    print(f'La ruta {ruta_destino} no corresponde a un directorio o esta corrupta')
                return False 
            
        except Exception as e:
            print(f'Ha ocurrido un error al borrar el fondo de la imagen: {e}')
            return False
    else:
        if aviso and not os.path.isdir(ruta_origen):
            print(f'La ruta {ruta_origen} no corresponde a una foto o esta corrupta')
        return False
    


def borrar_fondo_varias_fotos(ruta:str, numeracion_auto=False, aviso_fallos=False):
    """
    Función que borra el fondo de las imagenes halladas en un directorio, muy útil para quitar el fondo
    blanco de un retrato.
    Finalmente, las imágenes tratadas se dispondrán un directorio llamado 'img_sin_fondo_py' dentro del
    original dispuesto. En caso de existir ya el directorio, se preguntará si se desea elminiarlo, de manera recursiva,
    para crear otro posteriormente.

    Parameters:
    ----------
    - ruta (str): Ruta del directorio que contiene las imágenes.
    - numeracion_auto (bool): False por defecto. Numeracion automatica de los archivos.
    - aviso_fallos (bool): False por defecto. Variable que muestra fallos de excepción del tratado de cada foto
      en caso de que ocurran, ideal en caso de que la función no funcione correctamente.

    Returns:
    --------
    - Imágenes tratadas, dentro del directorio con el nombre 'img_sin_fondo_py' que estará contenido en la
      carpeta origen que hayamos indicado.
      En caso de error se mostrarán mensajes por consola.
    """

    #Normalizamos las rutas en caso de que no esten normalizadas
    ruta = os.path.normpath(ruta)

    #comprobamos que existe la ruta y que es un directorio
    if os.path.exists(ruta) and os.path.isdir(ruta):

        #obtenemos la nueva ruta donde guardaremos las imagenes modificadas
        nueva_ruta = _preparar_directorio(ruta, "img_sin_fondo_py")

        #Si se ha creado y dispuesto el directorio para el guardado de las imagenes, se continua
        if nueva_ruta != None:
            #contador que sirve para averiguar la cantidad de fotos que se han transformado
            cont = 1

            #iteramos los archivos para transformarlos
            for archivo in os.listdir(ruta):
                #obtenemos la direccion completa de la imagen para poder tratarla
                ruta_imagen = os.path.join(ruta, archivo)
                
                #creamos el nombre del archivo
                nombre_archivo = _poner_indice_imagenes(numeracion_auto, archivo, cont)

                if borrar_fondo_foto(ruta_imagen,nueva_ruta,nombre=nombre_archivo,aviso=aviso_fallos):
                    cont += 1

            print(f'Proceso terminado, {str(cont-1)} imagenes sin fondo de {_contar_imagenes_en_directorio(ruta)} imagenes encontradas')  

    else:
        print('El directorio introducido por parametro no existe o no es un directorio')

#----------------------Fin del codigo---------------------------------
ruta = r'C:\Users\Usuario\Desktop\aaa'

try:
    borrar_fondo_varias_fotos(ruta)
except TypeError as e:
    print(f"Error: Algunos parametros introducidos en la funcion son incorrectos o faltantes: {e}")


#--------------------------------------------------------------------------

#TODO instalar requerimientos automaticamente

#TODO retornar booleano y mensaje de texto (str) en los metodos en los que se pueda y revisar lo de los avisos (En una tupla?)
#TODO ¿Mirar velocidad de ejecucion y optimizar aquello que se pueda (poner funciones para aquellos trozos que se repitan?
        
#TODO Que el directorio de salida no se encuentre en el directorio de entrada (Que el directorio se proporcione de manera independiente, esto se hará cuando esté listo el lado del cliente)
        
#TODO Manipular rutas con pathlib?

#TODO poner if __name__ == '__main__' en caso de que ponga el uso por consola aquí más abajo?

#TODO ¿Comprobar que el directorio no esta vacio antes de trabajar con el?¿Hacerlo en el lado del cliente?

#TODO (En un mismo script o clase) Orden -> funciones independientes (las de arriba), funciones dependientes (las de abajo)







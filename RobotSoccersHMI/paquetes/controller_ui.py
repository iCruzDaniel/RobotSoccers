#Librerias y paquetes
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#import cv2
import sys

# Paquetes desarrollados
if __name__ == "__main__":
    from serialBridge import *
    from vent_cam import *
    from oculus import *
    from panel_control import *
else:
    from .serialBridge import *
    from .vent_cam import *
    from .oculus import *
    from .panel_control import *


#Inicializamos la aplicación
app = QtWidgets.QApplication([])

#instanciamos las vistas
vent_registros = uic.loadUi("../vistas/vista1.ui")
vent_juego = uic.loadUi("../vistas/vista2.ui")
vent_simulacion = uic.loadUi("../vistas/vista3.ui")


"""------------------------------------cntrl: VENTANA REGISTROS--------------------------------------------"""
# ---  config Iniciales
vent_registros.advertencia_registro.hide()

# --- funciones
def registrar_visitantes(): #registrar a los visitantes
    nombre_p1 = vent_registros.lineEdit_p1.text()
    nombre_p2 = vent_registros.lineEdit_p2.text()

    if len(nombre_p1)==0 or len(nombre_p2)==0:  #Validar registros
        vent_registros.advertencia_registro.show()
    else:
        vent_registros.hide()
        vent_juego.show()


# ------ botones
vent_registros.boton_registrar.clicked.connect(registrar_visitantes)
"""---------------------------------------- |||| ----------------------------------------"""



"""---------------------------------- cntrl: VENTANA DE JUEGO ------------------------------------------"""
# ---  config Iniciales
#Inicializamos controlador de partida
marcador = Marcador("visitantes", "Locales", vent_juego.puntaje_marcador)  #Objeto marcador
cronometro = Cronometro(label=vent_juego.cronometro) #Objeto Cronómetro

camara = Oculus() #Objeto para ventana visualizadora de la camara

vent_juego.menu.hide() #Esconder el menu principal

# --- funciones

#funcion para modificar el estado de baterías
def baterias(m1, m2):

    estados = { #Posibles estados de las baterías: 0% 20% 40% 60% 80% 100%
        0: QPixmap('../vistas/recursos/BAT0.png'),
        20: QPixmap('../vistas/recursos/BAT20.png'),
        40: QPixmap('../vistas/recursos/BAT40.png'),
        60: QPixmap('../vistas/recursos/BAT60.png'),
        80: QPixmap('../vistas/recursos/BAT80.png'),
        100: QPixmap('../vistas/recursos/BAT100.png')
    }

    # Establecer los estados en cada uno de los labels correspondientes
    vent_juego.bat_estado_m1.setPixmap(estados[m1])
    vent_juego.bat_estado_m2.setPixmap(estados[m2])
    
#Funcion para visualizar video
def Imageupd_slot(Image):
    vent_juego.vent_camara.setPixmap(QPixmap.fromImage(Image))

def play_video():
    camara.start()
    camara.Imageupdate.connect(Imageupd_slot)

def cancel():
    vent_juego.vent_camara.clear()
    camara.stop()

def salir():
    sys.exit()


#funcion para panel de control 
#(conectar al CORE)
def panel_control(opc):  
    operaciones = {
        1: cronometro.pausar_partido,
        2: cronometro.iniciar_partido,
        3: cronometro.detener_partido,
        4: cronometro.reiniciar_partido,
        5: vent_juego.menu.show

    }
    operaciones[opc]()


#funcion tabla registro de goles (conectar al CORE)
# ------------ marcador.anotar_gol(1)
def corregirGol(equipo, num):
    marcador.marcador[equipo] += num
    if marcador.marcador[0] < 0: marcador.marcador[0] =0
    if marcador.marcador[1] < 0: marcador.marcador[1] =0
    marcador.label.setText(f"{marcador.marcador[0]} - {marcador.marcador[1]}")

def refrescarPuertos():
    if vent_juego.lista_puertos.count() != 0: 
        vent_juego.lista_puertos.clear()
    vent_juego.lista_puertos.addItems(list_ports())

def conectarCOM():
    pCOM = vent_juego.lista_puertos.currentText()

    puerto = SerialConnection(pCOM)
    print(f"conectado {pCOM}")

# ------ botones
#Panel de contrl
vent_juego.boton_pausa.clicked.connect(lambda: panel_control(1))
vent_juego.boton_iniciar.clicked.connect(lambda: panel_control(2))
vent_juego.boton_detener.clicked.connect(lambda: panel_control(3))
vent_juego.boton_reinicio.clicked.connect(lambda: panel_control(4))
vent_juego.boton_menu.clicked.connect(lambda: panel_control(5))

#Menú Botones
vent_juego.boton_refrescar.clicked.connect(refrescarPuertos)
vent_juego.boton_locales_mas.clicked.connect(lambda: corregirGol(0, 1))
vent_juego.boton_locales_menos.clicked.connect(lambda: corregirGol(0, -1))
vent_juego.boton_visitantes_mas.clicked.connect(lambda: corregirGol(1, 1))
vent_juego.boton_visitantes_menos.clicked.connect(lambda: corregirGol(1, -1))

# ------ señales
#Menú señales
vent_juego.lista_puertos.currentIndexChanged.connect(conectarCOM)
"""-------------------------------------- |||| -----------------------------------------------"""



"""------------------------------------- cntrl: VENTANA DE SIMULACION ------------------------------------------"""

"""-------------------------------------- |||| ----------------------------------------------"""

play_video()

if __name__ == "__main__":
    baterias(20, 60) # BateriaMaquina1: 20%,  BateriaMaquina1: 60%,  
    #marcador.anotar_gol(0)

    #Motrar y ejecutar ventana
    #-vent_registros.show()
    vent_juego.show()
    #-vent_simulacion.show()
    #-app.exec()

    app.exec()

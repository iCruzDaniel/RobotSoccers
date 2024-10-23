#Librerias
import time

#Paquetes desarrollados
from paquetes.controller_ui import *
from paquetes.serialBridge import *
from paquetes.tree import *



#Ejecución del CORE:
if __name__ == "__main__":
    baterias(20, 60) # BateriaMaquina1: 20%,  BateriaMaquina1: 60%,  
    play_video()

    #Motrar y ejecutar ventana
    #-vent_registros.show()
    vent_juego.show()


    app.exec()

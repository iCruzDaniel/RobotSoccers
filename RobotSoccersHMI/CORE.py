#Librerias
import time

#Paquetes desarrollados
from paquetes.controller_ui import *
from paquetes.serialBridge import *
from paquetes.tree import *

arbol = Tree()

#Ejecución del CORE:
if __name__ == "__main__":
    #Intancias de la UI
    baterias(20, 60) # BateriaMaquina1: 20%,  BateriaMaquina1: 60%,  
    play_video()
    #Motrar y ejecutar ventana
    vent_juego.show()
    app.exec()
    
    
    while(True):
        band = True
        while(cronometro.is_running):
            #Varificar si es la conexión se ha restablcido o sigue en ejecución
            if band:
                print("Conectando al puerto serie...")
                puerto.connect()
                time.sleep(1)
                band=False
            #Evalua y manda la trama
            trama = "T" + arbol.eval(1) + "D2000" + "|"#arbol.eval(2)
            puerto.send_data(trama)
            time.sleep(0.1)
import cv2
import numpy as np
import cv2.aruco as aruco
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#Valores
exc = 75 #pixeles excedentes
init_x = 0
init_y = 0 + exc
ancho = 600
alto =  330
num_dispositivo = 0

class Oculus(QThread):
#    def __init__(self, num_dispositivo=0, init_x=0, init_y=0, ancho=720, alto=480):
        # Definir el área de interés
    area_inicio_x = init_x
    area_inicio_y = init_y
    area_ancho = ancho
    area_alto = alto
    num_dispositivo = num_dispositivo
    Imageupdate = pyqtSignal(QImage)

    area_local = (20, 20, 300, 320)  # (x_min, y_min, x_max, y_max)
    area_rival = (301, 20, 600, 320)  # (x_min, y_min, x_max, y_max)

    # Función para detectar el color rojo en la imagen
    def detectar_color_rojo(self, frame):
        # Convertir la imagen al espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Definir el rango de color rojo en HSV
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        
        # Crear una máscara para el color rojo
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        
        # Otro rango para tonos más claros de rojo
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        # Unir ambas máscaras
        mask = mask1 + mask2
        
        # Filtrar solo el color rojo de la imagen
        res = cv2.bitwise_and(frame, frame, mask=mask)
        
        return mask, res
    
    def Posicion_pelota(self, cx, cy):
        # Verificar si la pelota está en el área local
        if (self.area_local[0] <= cx <= self.area_local[2]) and (self.area_local[1] <= cy <= self.area_local[3]):
            return True  # Está en el área local
        
        # Verificar si la pelota está en el área rival
        if (self.area_rival[0] <= cx <= self.area_rival[2]) and (self.area_rival[1] <= cy <= self.area_rival[3]):
            return False  # Está en el área rival
        
        return None  # No está en ninguna de las áreas
    
    # Dimensiones de las porterías dentro del ROI
    porteria_ancho = 50  # Ajusta según el tamaño deseado de la portería
    porteria_alto = int(area_alto * 0.2)  # Altura de la portería

    def dibujar_porterias_y_determinar_proximidad(self, area_interes, objeto_centro):
        """
        Dibuja los cuadros izquierdo y derecho en el área de interés y determina la proximidad
        del objeto rojo detectado con respecto a cada uno de estos cuadros.
        """
        # Coordenadas de las porterías (cuadros) en la ROI
        porteria_izquierda_x = 10
        porteria_izquierda_y = (self.area_alto - self.porteria_alto) // 2
        porteria_derecha_x = self.area_ancho - self.porteria_ancho - 10
        porteria_derecha_y = porteria_izquierda_y

        # Dibujar el cuadro izquierdo en verde
        cv2.rectangle(area_interes, (porteria_izquierda_x, porteria_izquierda_y),
                      (porteria_izquierda_x + self.porteria_ancho, porteria_izquierda_y + self.porteria_alto), (0, 255, 0), 2)
        
        # Dibujar el cuadro derecho en azullll
        cv2.rectangle(area_interes, (porteria_derecha_x, porteria_derecha_y),
                      (porteria_derecha_x + self.porteria_ancho, porteria_derecha_y + self.porteria_alto), (255, 0, 0), 2)

        # Calcular los centros de cada portería
        centro_izquierda = (porteria_izquierda_x + self.porteria_ancho // 2, porteria_izquierda_y + self.porteria_alto // 2)
        centro_derecha = (porteria_derecha_x + self.porteria_ancho // 2, porteria_derecha_y + self.porteria_alto // 2)

        # Obtener la distancia euclidiana desde el objeto rojo detectado a cada cuadro
        distancia_izquierda = np.linalg.norm(np.array(objeto_centro) - np.array(centro_izquierda))
        distancia_derecha = np.linalg.norm(np.array(objeto_centro) - np.array(centro_derecha))

        # Determinar cuál cuadro está más cerca
        if distancia_izquierda < distancia_derecha:
            return "izquierda" #local
        else:
            return "derecha" # rival

    

    def run(self):
        self.hilo_corriendo = True
        cap = cv2.VideoCapture(0)

        # Definir el diccionario ArUco que se va a utilizar
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)

        # Crear el detector de parámetros
        parameters = cv2.aruco.DetectorParameters()

        # Iniciar la captura de la cámara
        cap = cv2.VideoCapture(self.num_dispositivo)

        while self.hilo_corriendo:
            ret, frame = cap.read()
            if ret:
                """Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #flip = cv2.flip(Image, 1)
                flip = Image
                convertir_QT = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_RGB888)
                pic = convertir_QT.scaled(720, 480, Qt.KeepAspectRatio)
                self.Imageupdate.emit(pic)"""

                # Convertir la imagen a escala de grises
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detectar marcadores ArUco
                corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
                
                # Recortar el área de interés
                area_interes = frame[self.area_inicio_y:self.area_inicio_y+self.area_alto, self.area_inicio_x:self.area_inicio_x+self.area_ancho]
                # Dibujar los marcadores detectados
                if ids is not None:
                    aruco.drawDetectedMarkers(frame, corners, ids)
                    
                    for marker_corners in corners:
                        # Calcular el centro del marcador
                        center = np.mean(marker_corners[0], axis=0)
                        cx, cy = int(center[0]), int(center[1])
                        
                        # Dibujar un círculo en el centro del marcador
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                        
                        # Mostrar las coordenadas del marcador ArUco
                        cv2.putText(frame, f'({cx},{cy})', (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                        # Llamar a la función de proximidad y obtener el cuadro más cercano
                        cuadro_cercano = self.dibujar_porterias_y_determinar_proximidad(area_interes, (cx, cy))
                        cv2.putText(frame, f'Mas cerca del cuadro {cuadro_cercano}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        print (f"el jugador esta en: {cuadro_cercano}")

                
                # Detectar el color rojo en el área de interés
                mask, res = self.detectar_color_rojo(area_interes)
                
                # Encontrar los contornos de los objetos rojos
                contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contorno in contornos:
                    # Ignorar pequeños contornos
                    if cv2.contourArea(contorno) < 500:
                        continue
                
                    # Obtener las coordenadas del centro del objeto rojo
                    M = cv2.moments(contorno)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        # Llamar a la función Posicion_pelota para determinar la ubicación de la pelota
                        posicion = self.Posicion_pelota(cx, cy)
                        if posicion is not None:
                            estado_area = "Local" if posicion else "Rival" # if po
                            print(f"La pelota está en el área: {estado_area}")

                        # Dibujar un círculo en el centro del objeto rojo
                        cv2.circle(area_interes, (cx, cy), 5, (0, 0, 0), -1)
                        # Mostrar las coordenadas en la ventana
                        cv2.putText(frame, f'({cx},{cy})', (self.area_inicio_x + cx, self.area_inicio_y + cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Dibujar el plano cartesiano en el área de interés
                cv2.line(frame, (self.area_inicio_x, self.area_inicio_y + self.area_alto // 2), (self.area_inicio_x + self.area_ancho, self.area_inicio_y + self.area_alto // 2), (255, 255, 255), 2)  # Eje X
                cv2.line(frame, (self.area_inicio_x + self.area_ancho // 2, self.area_inicio_y), (self.area_inicio_x + self.area_ancho // 2, self.area_inicio_y + self.area_alto), (255, 255, 255), 2)  # Eje Y
                # Dibujar el contorno de la ROI
                cv2.rectangle(frame, (self.area_inicio_x, self.area_inicio_y), (self.area_inicio_x + self.area_ancho, self.area_inicio_y + self.area_alto), (255, 0, 0), 2)  # Cuadro azul
                
                # Preparación de Imagen que va a la ventana de visualización
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #flip = cv2.flip(Image, 1)
                flip = Image
                convertir_QT = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_RGB888)
                pic = convertir_QT.scaled(720, 480, Qt.KeepAspectRatio)
                self.Imageupdate.emit(pic)
            else:
                break



    def stop(self):
        self.hilo_corriendo = False
        self.quit()
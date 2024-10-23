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

                        # Recortar el área de interés
                area_interes = frame[self.area_inicio_y:self.area_inicio_y+self.area_alto, self.area_inicio_x:self.area_inicio_x+self.area_ancho]
                
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

    """----------------------------------------------------------"""
   
"""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convertir la imagen a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar marcadores ArUco
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        
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
        
        # Recortar el área de interés
        area_interes = frame[area_inicio_y:area_inicio_y+area_alto, area_inicio_x:area_inicio_x+area_ancho]
        
        # Detectar el color rojo en el área de interés
        mask, res = detectar_color_rojo(area_interes)
        
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
                
                # Dibujar un círculo en el centro del objeto rojo
                cv2.circle(area_interes, (cx, cy), 5, (0, 0, 0), -1)
                
                # Mostrar las coordenadas en la ventana
                cv2.putText(frame, f'({cx},{cy})', (area_inicio_x + cx, area_inicio_y + cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Dibujar el plano cartesiano en el área de interés
        cv2.line(frame, (area_inicio_x, area_inicio_y + area_alto // 2), (area_inicio_x + area_ancho, area_inicio_y + area_alto // 2), (255, 255, 255), 2)  # Eje X
        cv2.line(frame, (area_inicio_x + area_ancho // 2, area_inicio_y), (area_inicio_x + area_ancho // 2, area_inicio_y + area_alto), (255, 255, 255), 2)  # Eje Y
        
        # Dibujar el contorno de la ROI
        cv2.rectangle(frame, (area_inicio_x, area_inicio_y), (area_inicio_x + area_ancho, area_inicio_y + area_alto), (255, 0, 0), 2)  # Cuadro azul
        




        # Mostrar la imagen
        cv2.imshow('Deteccion de Color Rojo y ArUco', frame)
        
        # Salir al presionar 'f'
        if cv2.waitKey(1) & 0xFF == ord('f'):
            break
            
    """

    # Liberar la cámara y cerrar las ventanas

    #cap.release()
    #cv2.destroyAllWindows()

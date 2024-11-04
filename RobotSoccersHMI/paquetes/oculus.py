import cv2
import numpy as np
import cv2.aruco as aruco
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

#Valores iniciales del ROI
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

    # Dimensiones de las porterías dentro del ROI
    porteria_ancho = 50  # Ajusta según el tamaño deseado de la portería
    porteria_alto = int(area_alto * 0.2)  # Altura de la portería

    #zona de poseción pelota
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

    def mas_cerca_arco_local(self, area_interes, ids, centros):
        """
        Dibuja los cuadros izquierdo y derecho en el área de interés y determina
        cuál marcador está más cerca de cada portería.
        """
        # Coordenadas de las porterías (cuadros) en la ROI
        porteria_izquierda_x = 10
        porteria_izquierda_y = (self.area_alto - self.porteria_alto) // 2
        porteria_derecha_x = self.area_ancho - self.porteria_ancho - 10
        porteria_derecha_y = porteria_izquierda_y

        # Dibujar el cuadro izquierdo en verde
        cv2.rectangle(area_interes, (porteria_izquierda_x, porteria_izquierda_y),
                      (porteria_izquierda_x + self.porteria_ancho, porteria_izquierda_y + self.porteria_alto), (0, 255, 0), 2)
        
        # Dibujar el cuadro derecho en rojo
        cv2.rectangle(area_interes, (porteria_derecha_x, porteria_derecha_y),
                      (porteria_derecha_x + self.porteria_ancho, porteria_derecha_y + self.porteria_alto), (255, 0, 0), 2)

        # Calcular los centros de cada portería
        centro_izquierda = (porteria_izquierda_x + self.porteria_ancho // 2, porteria_izquierda_y + self.porteria_alto // 2)
        centro_derecha = (porteria_derecha_x + self.porteria_ancho // 2, porteria_derecha_y + self.porteria_alto // 2)

        # Variables para almacenar el marcador más cercano a cada portería
        id_mas_cercano_izquierda = None
        id_mas_cercano_derecha = None
        distancia_min_izquierda = float('inf')
        distancia_min_derecha = float('inf')

        # Iterar sobre cada marcador detectado
        for i, centro in enumerate(centros):
            # Calcular la distancia del marcador a cada portería
            distancia_izquierda = np.linalg.norm(np.array(centro) - np.array(centro_izquierda))
            distancia_derecha = np.linalg.norm(np.array(centro) - np.array(centro_derecha))
            
            # Verificar si es el más cercano a la portería izquierda
            if distancia_izquierda < distancia_min_izquierda:
                distancia_min_izquierda = distancia_izquierda
                id_mas_cercano_izquierda = ids[i][0]  # ID del marcador

            # Verificar si es el más cercano a la portería derecha
            if distancia_derecha < distancia_min_derecha:
                distancia_min_derecha = distancia_derecha
                id_mas_cercano_derecha = ids[i][0]  # ID del marcador

        # Devolver el marcador más cercano a cada portería y sus distancias
        return id_mas_cercano_izquierda, distancia_min_izquierda, id_mas_cercano_derecha, distancia_min_derecha
        
         
         # Función para calcular la distancia entre dos puntos
       
    def comparar_distancia_arucos(self, ids, centros, id1, id2, pelota_pos):
    # Verificar que ambos ID estén en la lista de marcadores detectados
        pos_id1 = None
        pos_id2 = None

        for i, id_ in enumerate(ids):
            if id_[0] == id1:
                pos_id1 = centros[i]
            elif id_[0] == id2:
                pos_id2 = centros[i]

        # Si alguno de los IDs no fue encontrado, devolver None
        if pos_id1 is None or pos_id2 is None:
            return None, None  # No se pudo realizar la comparación

        # Calcular la distancia desde cada ID al objeto rojo
        distancia_id1 = np.linalg.norm(np.array(pos_id1) - np.array(pelota_pos))
        distancia_id2 = np.linalg.norm(np.array(pos_id2) - np.array(pelota_pos))

         # Determinar cuál ID está más cerca del objeto rojo
        if distancia_id1 < distancia_id2:
            return id1, distancia_id1
        else:
            return id2, distancia_id2
        
    def angulo_frente(self, frente_robot, robot_pos, pelota_pos):
        #Vector desde el robot hacia la pelota
        vector_pelota = np.array([pelota_pos[0] - robot_pos[0], pelota_pos[1] - robot_pos[1]])
        if np.linalg.norm(vector_pelota) == 0: #Evitar divisiones por cero
            return 0
        vector_pelota = vector_pelota/np.linalg.norm(vector_pelota) #normalizar vector
        
        #Calculo del angulo entre el frente del robot y la pelota
        angulo = np.arccos(np.clip(np.dot(frente_robot, vector_pelota), -1.0, 1.0))
        angulo = math.degrees(angulo) #convertir de radianes a grados
        
        #Determinar el signo del angulo basado en el producto cruzado        
        signo = np.cross(frente_robot,vector_pelota)
        if signo < 0:
            angulo = -angulo  # Ángulo negativo si es hacia la izquierda
            
        return angulo

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

                # Convertir la imagen a escala de grises
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detectar marcadores ArUco
                corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
                
                # Recortar el área de interés
                area_interes = frame[self.area_inicio_y:self.area_inicio_y+self.area_alto, self.area_inicio_x:self.area_inicio_x+self.area_ancho]
                
                #Inicializar centros como lista
                centros =[] #array para la funcion

                # Dibujar los marcadores detectados
                if ids is not None:
                    aruco.drawDetectedMarkers(frame, corners, ids)
                    
                    for marker_corners in corners:
                        # Calcular el centro del marcador
                        center = np.mean(marker_corners[0], axis=0)

                        px, py = int(center[0]), int(center[1]) #cambiar nombre
                        centros.append((px, py)) #array para la funcion

                        #Calcular el vector  de direccion frontal (El frente se asume entre las esquinas 0 y 3)
                        front_direccion =  marker_corners[0][0] - marker_corners[0][3]
                        front_direccion = front_direccion/np.linalg.norm(front_direccion) # normalizar el vector
                        
                        robot_pos = (px,py)
                        if pelota_pos is not None and robot_pos is not None:
                            #Llamado de la funcion 
                            angulo_diferencia = self.angulo_frente(front_direccion,(px,py),pelota_pos)
                            
                            #Print angulo_diferencia
                            #print(f"Angulo del frente del robot respecto a la pelota:{angulo_diferencia} grados")
                            
                            

                        front_point = (int(px + front_direccion[0]*30),int(py + front_direccion[1]*30))
                        cv2.line(frame,(px,py),front_point, (0,255,255),2) # Dibujar la linea para indicar el frente

                        # Dibujar un círculo en el centro del marcador
                        cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)
                        
                        # Mostrar las coordenadas del marcador ArUco
                        cv2.putText(frame, f'({px},{py})', (px + 5, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                      
                     # Llamar a la función de proximidad y obtener los marcadores más cercanos a cada portería
                    id_izquierda, dist_izquierda, id_derecha, dist_derecha = self.mas_cerca_arco_local(area_interes, ids, centros)
                    
                    # Mostrar el ID y la distancia de los marcadores más cercanos en pantalla
                    cv2.putText(frame, f'Más cercano a izquierda: ID {id_izquierda} ({dist_izquierda:.2f} px)', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f'Más cercano a derecha: ID {id_derecha} ({dist_derecha:.2f} px)', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    
                    #Print mas_cerca_arco_local
                    #print("id izq=",id_izquierda, dist_izquierda, "id dere=", id_derecha, dist_derecha)    
                    

                # Detectar el color rojo en el área de interés
                mask, res = self.detectar_color_rojo(area_interes)
                
                # Encontrar los contornos de los objetos rojos
                contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                pelota_pos= None #array posición pelota 
                
                for contorno in contornos:
                    # Ignorar pequeños contornos
                    if cv2.contourArea(contorno) < 500:
                        continue
                
                    # Obtener las coordenadas del centro del objeto rojo
                    M = cv2.moments(contorno)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        pelota_pos=(cx,cy) #posicion de la pelota 
                        

                        # Llamar a la función Posicion_pelota para determinar la ubicación de la pelota
                        posicion = self.Posicion_pelota(cx, cy)
                        if posicion is not None:
                            estado_area = "Local" if posicion else "Rival" 
                            
                            
                            #Print Posicion_pelota
                            #print(f"La pelota está en el área: {estado_area}")

                        # Dibujar un círculo en el centro del objeto rojo
                        cv2.circle(area_interes, (cx, cy), 5, (0, 0, 0), -1)
                        # Mostrar las coordenadas en la ventana
                        cv2.putText(frame, f'({cx},{cy})', (self.area_inicio_x + cx, self.area_inicio_y + cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        
                        if centros:
                            # Comparar distancia entre IDs específicos y el objeto rojo
                            id_mas_cercano, distancia = self.comparar_distancia_arucos(ids, centros, 1, 0, pelota_pos)
                            angulo_orientacion = self.angulo_frente(front_direccion,(px,py),pelota_pos)
                            
                            #Umbral del angulo (Se puede modificar si es necesario)
                            angulo_umbral = -10 #grados
                            angulo_umbral1 = 10 #grados
                    
                            # Mostrar en pantalla cuál ID está más cerca del objeto rojo
                            if id_mas_cercano is not None:
                                cv2.putText(frame, f'ID {id_mas_cercano} está más cerca del objeto rojo ({distancia:.2f}px)', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                               
                                #print Comparar_distancia_arucos + angulo_frente (Posesion del balon)
                                #print(f"Id mas cercano {id_mas_cercano}")
                                
                            
                            if angulo_umbral <= angulo_orientacion <= angulo_umbral1:
                                print(f"El robot con ID {id_mas_cercano} tiene la posesión del balón.")
                            else:
                                print(f"El robot con ID {id_mas_cercano} esta cerca, pero no posee el balon.")
                                

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
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
    Imageupdate = pyqtSignal(QImage)
    def __init__(self, num_dispositivo=0, init_x=0, init_y=75, ancho=600, alto=330):
        super().__init__()
        # Inicialización del área de interés
        self.area_inicio_x = init_x
        self.area_inicio_y = init_y
        self.area_ancho = ancho
        self.area_alto = alto
        self.num_dispositivo = num_dispositivo
        self.frame = None  # Inicializar el frame a None
        self.robot_id = 0 # el arbol debe de enviar cual id se este evaluando
        
        # Variables para el área local y rival
        self.area_local = (20, 20, 300, 320) #xmin ymin, xmax ymax
        self.area_rival = (301, 20, 600, 320) #xmin ymin, xmax ymax

    def detectar_color_pelota(self):  #detecta el color de la pelota y retorna la mask y el res
        """
        Detecta el color rojo en el atributo 'frame' y devuelve la máscara y el resultado filtrado.
        """
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        
        # Definir el rango de color rojo en HSV
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        
        # Otro rango para tonos más claros de rojo
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        # Unir ambas máscaras y aplicar al frame
        mask = mask1 + mask2
        #sacar el color rojo de la imagen
        res = cv2.bitwise_and(self.frame, self.frame, mask=mask)
        
        return mask, res

    def detectar_arucos(self): #detecta los codigos arucos, y su linea de frente, retorna los centroides y los ID
        """
        Detecta los códigos ArUco en el frame y devuelve los centroides y IDs de los códigos detectados.
        """
        # Convertir la imagen a escala de grises y definir el diccionario ArUco
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_50)
        parameters = aruco.DetectorParameters()

        # Detectar marcadores ArUco
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        
        centros = []
        front_point = []
        if ids is not None:
            for marker_corners in corners:
                center = np.mean(marker_corners[0], axis=0)
                px, py = int(center[0]), int(center[1])
                centros.append((px, py))
                aruco.drawDetectedMarkers(self.frame, corners, ids)

                #Calcular el vector  de direccion frontal (El frente se asume entre las esquinas 0 y 3)
                front_direccion =  marker_corners[0][0] - marker_corners[0][3] #esquinas
                front_direccion = front_direccion/np.linalg.norm(front_direccion) # normalizar el vector
                front_point = (int(px + front_direccion[0]*30),int(py + front_direccion[1]*30))
                cv2.line(self.frame,(px,py),front_point, (0,255,255),2) # Dibujar la linea para indicar el frente
        
        return centros, ids, front_point

    def detectar_centroides_pelota(self, mask, res): #detecta los centroides de la pelota y retorna su centroide
        """
        Detecta los centroides de los objetos rojos en el área de interés usando la máscara.
        """
        contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        centroides = []
        for contorno in contornos: 
                if cv2.contourArea(contorno) < 500:
                    continue  # Ignorar contornos pequeños
                
                # Calcular el centroide del contorno
                x, y, ancho, alto = cv2.boundingRect(contorno)
                # se extraen las coordenadas del recuadro
                xi = x # coordenada x inicial
                yi = y #coordenada en y inicial
                xf = x + ancho # coordenada x final
                yf = y + alto # coordenada en y final
                # dibujamos el rectangulo
                cv2.rectangle(self.frame, (xi,yi), (xf, yf),(255,255,0),2)
                # calculamos el centroide
                cx = int((xi+xf)/2) #centroide en x
                cy = int((yi+yf)/2) # centroide en y
                centroides.append((cx, cy))
                cv2.circle(self.frame,(cx,cy),1,(0,0,0), 2)
                # mostrar las coordenadas
                texto_coordenadas = f" ({cx}, {cy})" # coordenadas en forma de texto para mostrar en el frame
                # Añade el texto al frame en una posición deseada
                cv2.putText(self.frame, texto_coordenadas, (cx + 15, cy+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return centroides
    


    

     
    # ----------------PRIMERA EVALUACIÓN: Posicion de la pelota--------------------------------   
    
    #primera evaluación mira en que zona esta la pelota, rival o local.
    def Posicion_pelota(self): 
        # Detectar el color de la pelota en el frame
        mask, res = self.detectar_color_pelota()

        # Encontrar el centroide de la pelota
        centroides_pelota = self.detectar_centroides_pelota(mask, res)

        # Verificar si se encontró la pelota
        if not centroides_pelota:
            return None  # No hay pelota detectada

        # Obtener el centroide de la pelota
        cx, cy = centroides_pelota[0]  # Considerar solo el primer centroide si hay varios

        # Verificar si la pelota está en el área local
        if (self.area_local[0] <= cx <= self.area_local[2]) and (self.area_local[1] <= cy <= self.area_local[3]):
            return True  # Está en el área local

        # Verificar si la pelota está en el área rival
        if (self.area_rival[0] <= cx <= self.area_rival[2]) and (self.area_rival[1] <= cy <= self.area_rival[3]):
            return False  # Está en el área rival





#-------------------SEGUNDA EVALUACIÓN: Mas cerca al arco Local-----------------------

    #segunda evaluación mira cual robot esta mas cerca al arco de la zona local
    def mas_cerca_arco_local(self): 
        # Determinar si el arco "local" es el izquierdo o el derecho
        pelota_en_area_local = self.Posicion_pelota()
        #dimenciones del arco "local"

        # Dimensiones de las porterías dentro del ROI
        porteria_ancho = 50  # Ajusta según el tamaño deseado de la portería
        porteria_alto = int(self.area_alto * 0.2)  # Altura de la portería
        
        if pelota_en_area_local:
            centro_arco = (10 + porteria_ancho // 2, (self.area_alto - porteria_alto) // 2)  # Coordenadas del arco izquierdo
        else:
            centro_arco = (self.area_ancho - porteria_ancho // 2 - 10, (self.area_alto - porteria_alto) // 2)  # Coordenadas del arco derecho

        # Detectar marcadores ArUco
        centros_arucos, ids_arucos, frente_robot= self.detectar_arucos()

        if ids_arucos is None:
            return False  # No hay marcadores detectados, devolver False

        # Inicializar variables para almacenar el marcador más cercano al arco
        id_mas_cercano = None
        distancia_min = float('inf')

        # Iterar sobre cada marcador detectado
        for i, centro in enumerate(centros_arucos):
            distancia_arco = np.linalg.norm(np.array(centro) - np.array(centro_arco))
            
            # Verificar si es el más cercano al arco "local"
            if distancia_arco < distancia_min:
                distancia_min = distancia_arco
                id_mas_cercano = ids_arucos[i][0]

        # Retornar True si el robot_id actual es el más cercano al arco "local" determinado
        return id_mas_cercano == self.robot_id
    

#-------------------TERCERA EVALUACIÓN: Mas cerca al arco Local-------------------------

    #tercera evaluación determina que robot esta mas cerca de la pelota
    def mas_cerca_pelota(self):
        """
        Determina si el robot con ID específico (self.robot_id) es el más cercano a la pelota.
        Retorna True si el robot_id está más cerca de la pelota, False si no lo está, y None si alguno de los IDs no está presente.
        """
        # Detectar el color de la pelota
        mask, res = self.detectar_color_pelota()

        # Detectar los centroides de la pelota en la ROI
        pelota_centroides = self.detectar_centroides_pelota(mask, res)
        if not pelota_centroides:
            return None  # No se encontró pelota

        # Considerar el primer centro de la pelota detectado
        pelota_pos = pelota_centroides[0]
        # Detectar los códigos ArUco en la ROI
        centros_arucos, ids_arucos, frente_robot = self.detectar_arucos()
        if ids_arucos is None:
            return None  # No se encontraron marcadores ArUco

        # Verificar que ambos IDs (0 y 1) están presentes y obtener sus posiciones
        pos_id1 = None
        pos_id2 = None
        for i, id_ in enumerate(ids_arucos):
            if id_[0] == 0:
                pos_id1 = centros_arucos[i]
            elif id_[0] == 1:
                pos_id2 = centros_arucos[i]

        # Si alguno de los IDs no está presente, retornar None
        if pos_id1 is None or pos_id2 is None:
            return None

        # Calcular distancias de los IDs a la pelota
        distancia_id1 = np.linalg.norm(np.array(pos_id1) - np.array(pelota_pos))
        distancia_id2 = np.linalg.norm(np.array(pos_id2) - np.array(pelota_pos))

        # Determinar si el robot evaluado es el más cercano a la pelota
        if self.robot_id == 0:
            return distancia_id1 <= distancia_id2
        elif self.robot_id == 1:
            return distancia_id2 < distancia_id1
        else:
            return None  # ID no válido para esta evaluación
            
        #--------------------------------QUINTA EVALUACIÓN: Alineado Pelota---------------------------

    #quinta evaluación, cuarta función, comprueba que el robot a evaluar este alineado con la pelota.    
    def alineado_pelota(self):
        """
        Determina si el robot está alineado con la pelota basándose en los centroides (x, y).
        Retorna True si está alineado, False si no lo está.
        """
        # Detectar la pelota en el frame actual
        mask, res = self.detectar_color_pelota()
        pelota_centroides = self.detectar_centroides_pelota(mask, res)

        # Detectar los códigos ArUco en el frame actual
        centros_arucos, ids_arucos, _ = self.detectar_arucos()

        # Verificar que haya pelota y robots detectados
        if not pelota_centroides or ids_arucos is None:
            return False  # No hay pelota o robots detectados

        # Obtener el centroide de la primera pelota detectada
        pelota_pos = np.array(pelota_centroides[0])

        # Buscar el centroide del robot con el ID especificado
        for i, id_ in enumerate(ids_arucos):
            if id_[0] == self.robot_id:  # Encontrar el ID del robot evaluado
                robot_pos = np.array(centros_arucos[i])

                # Definir tolerancias para la alineación
                tolerancia_y = 10  # Desviación aceptada en el eje Y (horizontal)
                tolerancia_x = 10  # Desviación aceptada en el eje X (vertical)
                distancia_minima = 20  # Distancia mínima en el otro eje para evitar falsos positivos

                # Evaluar alineación en el eje Y (horizontal)
                alineado_y = abs(pelota_pos[1] - robot_pos[1]) <= tolerancia_y
                suficientemente_lejos_x = abs(pelota_pos[0] - robot_pos[0]) > distancia_minima

                # Evaluar alineación en el eje X (vertical)
                alineado_x = abs(pelota_pos[0] - robot_pos[0]) <= tolerancia_x
                suficientemente_lejos_y = abs(pelota_pos[1] - robot_pos[1]) > distancia_minima

                # Retornar True si está alineado en cualquier eje y suficientemente lejos en el otro eje
                if (alineado_y and suficientemente_lejos_x) or (alineado_x and suficientemente_lejos_y):
                    return True  # Está alineado en al menos uno de los ejes
                else:
                    return False  # No está alineado en ninguno de los ejes

        return False  # Si el robot_id no está presente en los IDs detectados

    
    #-------------------------------Cuarta EVALUACIÓN: Posesión Pelota---------------
    
    #rectifica que el robot  a evaluar tenga la pelota
    def posesion_pelota(self):
        # Detectar la pelota en el frame actual
        mask, res = self.detectar_color_pelota()  # Detección de la pelota para actualizar la máscara interna
        pelota_centroides = self.detectar_centroides_pelota(mask, res)

        # Verificar si la pelota está presente
        if not pelota_centroides:
            return None  # No se detectó la pelota

        pelota_pos = pelota_centroides[0]  # Suponemos una sola pelota, tomamos la primera

        # Detectar ArUcos en el frame actual
        centros_arucos, ids_arucos, frente = self.detectar_arucos()

        # Verificar si hay códigos QR
        if ids_arucos is None or len(ids_arucos) == 0:
            return None  # No se detectaron ArUcos

        # Iterar sobre los ID y centros detectados para identificar el ID solicitado
        for i, (id_, centro) in enumerate(zip(ids_arucos, centros_arucos)):
            if id_ == self.robot_id:
                robot_pos = centro

                # Verificar si el robot está alineado con la pelota
                alineado = self.alineado_pelota()
                if alineado is not True:
                    return False  # No está alineado, entonces no tiene posesión

                # Calcular la distancia entre el robot y la pelota
                distancia = np.linalg.norm(np.array(robot_pos) - np.array(pelota_pos))

                # Definir umbral de distancia para considerar posesión de la pelota
                distancia_umbral = 20  # Píxeles
                if distancia < distancia_umbral:
                    return True  # El robot tiene posesión de la pelota

                # Si la distancia no es suficiente
                return False

        return None  # No se encontró el ID específico en los detectados
    
    
    #---------------------------SEXTA EVALUACIÓN: Desplazado hacia....----------------------------

    #indica si el robot tiene que girar hacia la izquierda o hacia la derecha
    def desplazado_hacia(self):
    # Detectar ArUco para obtener los frentes y posiciones
        centros_arucos, ids_arucos, frente_robot = self.detectar_arucos()

    # Verificar si hay marcadores ArUco detectados
        if ids_arucos is None:
            return None  # No hay ArUcos detectados

    # Verificar si el id_robot está presente
        for i, id_ in enumerate(ids_arucos):
            if id_[0] == self.robot_id:  # Encontrar el ID del robot evaluado
                robot_pos = np.array(centros_arucos[i])

                # Detectar la posición de la pelota
                mask, res = self.detectar_color_pelota()
                pelota_centroides = self.detectar_centroides_pelota(mask, res)
                if pelota_centroides:
                    pelota_pos = pelota_centroides[0]  # Suponemos una única pelota detectada

                    # Calcular el ángulo entre el frente del robot y la pelota
                    vector_pelota = np.array([pelota_pos[0] - robot_pos[0], pelota_pos[1] - robot_pos[1]])
                    vector_pelota = vector_pelota / np.linalg.norm(vector_pelota)
                    angulo = np.arccos(np.clip(np.dot(frente_robot, vector_pelota), -1.0, 1.0))
                    angulo = math.degrees(angulo)

                    # Determinar el signo del ángulo
                    signo = np.cross(frente_robot, vector_pelota)

                    # Verificar hacia dónde está desalineado el robot
                    if signo > 0:
                        return True  # Desalineado hacia la derecha, sentido horario
                    else:
                        return False  # Desalineado hacia la izquierda, sentido antihorario

        return None  # Si no se cumplen las condiciones anteriores
    

    #Función RUN
    
    def run(self):

        self.hilo_corriendo = True
        cap = cv2.VideoCapture(self.num_dispositivo)

        while self.hilo_corriendo:
            ret, self.frame = cap.read()
            if ret:
                # Actualizar el frame actual en el objeto
                # Definir la ROI sobre el frame
                area_interes = self.frame[self.area_inicio_y:self.area_inicio_y + self.area_alto, self.area_inicio_x:self.area_inicio_x + self.area_ancho]
            
                # Aplicar la detección de color de la pelota
                mask, res = self.detectar_color_pelota()
            
                # Detectar los centroides de los objetos rojos en la máscara
                centroides_pelota = self.detectar_centroides_pelota(mask, res)
            
                # Detectar los códigos ArUco
                centros_arucos, ids_arucos, frente_pelota = self.detectar_arucos()
                
                posicion = self.Posicion_pelota()
                estado_area = "Local" if posicion else "Rival"
                #print(f"La pelota está en el área: {estado_area}")
                
                #cual robot esta mas cerca al arco
                es_mas_cercano_arco_local = self.mas_cerca_arco_local()
                if es_mas_cercano_arco_local:
                    #print(f"El robot con ID {self.robot_id} es el más cercano al arco 'local'")
                    cv2.putText(area_interes, f"Robot {self.robot_id} cerca del arco local", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    #print(f"El robot con ID {self.robot_id} NO es el más cercano al arco 'local'")
                    cv2.putText(area_interes, f"Robot {self.robot_id} no cerca del arco local", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Evaluar si el robot actual (self.robot_id) es el más cercano a la pelota
                es_mas_cercano = self.mas_cerca_pelota()
                #id_texto = f'ID {self.robot_id} esta mas cerca del objeto rojo' if es_mas_cercano else f'ID {self.robot_id} no es el mas cercano'
                #cv2.putText(area_interes, id_texto, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                alineado_pelota= self.alineado_pelota()
                
                posesion_pelota=self.posesion_pelota()

                desplazado_hacia= self.desplazado_hacia()
                if desplazado_hacia is True:
                    print("girar derecha")
                if desplazado_hacia is False:
                    print("desplazado hacia la izquierda")

                
                
                # Visualizar los resultados en la ROI
                
            # Dibujar el plano cartesiano en el área de interés
                
                #dibujar  ROI
                # Dibujar el plano cartesiano en la ROI
                cv2.line(area_interes, (0, self.area_alto // 2), (self.area_ancho, self.area_alto // 2), (255, 255, 255), 2)  # Eje X
                cv2.line(area_interes, (self.area_ancho // 2, 0), (self.area_ancho // 2, self.area_alto), (255, 255, 255), 2)  # Eje Y
                    
                        # Dibujar el contorno de la ROI en el frame completo
                cv2.rectangle(self.frame, (self.area_inicio_x, self.area_inicio_y), (self.area_inicio_x + self.area_ancho, self.area_inicio_y + self.area_alto), (255, 0, 0), 2)  # Cuadro azul
                        
                        # Visualizar en ventana
                Image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                flip = Image
                convertir_QT = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_RGB888)
                pic = convertir_QT.scaled(720, 480, Qt.KeepAspectRatio)
                self.Imageupdate.emit(pic)
            

    def stop(self):
        self.hilo_corriendo = False
        self.quit()
        #actualizado
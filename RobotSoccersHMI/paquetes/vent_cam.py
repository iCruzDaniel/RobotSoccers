from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2

class Camara(QThread):
    Imageupdate = pyqtSignal(QImage)

    def run(self):
        self.hilo_corriendo = True
        cap = cv2.VideoCapture(0)
        
        while self.hilo_corriendo:
            ret, frame = cap.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #flip = cv2.flip(Image, 1)
                flip = Image
                convertir_QT = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_RGB888)
                pic = convertir_QT.scaled(720, 480, Qt.KeepAspectRatio)
                self.Imageupdate.emit(pic)
    
    def stop(self):
        self.hilo_corriendo = False
        self.quit()
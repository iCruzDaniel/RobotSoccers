import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class Cronometro:
    def __init__(self, minutos, segundos, label):
        self.total_time = minutos * 60 + segundos  # Convierte a segundos
        self.remaining_time = self.total_time
        self.is_running = False
        self.is_paused = False
        self.stop_thread = False  # Bandera para detener el hilo
        self.timer_thread = None
        self.label = label  # QLabel donde se mostrará el cronómetro

    def iniciar(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.stop_thread = False
            if self.timer_thread is None or not self.timer_thread.is_alive():
                self.timer_thread = threading.Thread(target=self._run_timer)
                self.timer_thread.start()

    def _run_timer(self):
        while self.is_running and self.remaining_time > 0 and not self.stop_thread:
            if not self.is_paused:
                mins, secs = divmod(self.remaining_time, 60)
                time_str = f"{mins:02d}:{secs:02d}"
                self.label.setText(f"Tiempo restante: {time_str}")  # Actualiza el QLabel
                time.sleep(1)
                self.remaining_time -= 1
        if self.remaining_time == 0 and not self.stop_thread:
            self.label.setText("¡Tiempo terminado!")
        self.is_running = False

    def pausar(self):
        if self.is_running:
            self.is_paused = True

    def continuar(self):
        if self.is_paused:
            self.is_paused = False

    def detener(self):
        self.is_running = False
        self.is_paused = False
        self.label.setText("Cronómetro detenido")

    def detener_hilo(self):
        """Detiene el hilo de manera segura"""
        self.stop_thread = True
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()  # Espera a que el hilo termine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Crear el QLabel donde se mostrará la cuenta regresiva
        self.label = QLabel("00:00", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")

        # Crear los botones de control
        self.start_button = QPushButton("Iniciar", self)
        self.start_button.clicked.connect(self.iniciar_cronometro)

        self.pause_button = QPushButton("Pausar", self)
        self.pause_button.clicked.connect(self.pausar_cronometro)

        self.stop_button = QPushButton("Detener", self)
        self.stop_button.clicked.connect(self.detener_cronometro)

        # Organizar los widgets en un layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Crear una instancia de Cronometro
        self.cronometro = Cronometro(1, 30, self.label)  # 1 minuto y 30 segundos de cuenta regresiva

    def iniciar_cronometro(self):
        self.cronometro.iniciar()

    def pausar_cronometro(self):
        self.cronometro.pausar()

    def detener_cronometro(self):
        self.cronometro.detener()

    def closeEvent(self, event):
        """Sobrescribe el evento de cierre para detener los hilos"""
        self.cronometro.detener_hilo()  # Detiene el hilo del cronómetro
        event.accept()  # Permite cerrar la ventana


# Crear la aplicación y la ventana principal
app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle("Cronómetro en QLabel")
window.resize(300, 200)
window.show()
sys.exit(app.exec_())

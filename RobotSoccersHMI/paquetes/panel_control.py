import threading
import time 

class Cronometro:
    def __init__(self, label, minutos=2, segundos=0):
        self.total_time = minutos * 60 + segundos  # Convierte a segundos
        self.remaining_time = self.total_time
        self.is_running = False
        self.is_paused = False
        self.timer_thread = None
        self.label = label  # QLabel donde se mostrará el cronómetro

    def iniciar_partido(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            if self.timer_thread is None or not self.timer_thread.is_alive():
                self.timer_thread = threading.Thread(target=self._run_timer)
                self.timer_thread.start()

    def _run_timer(self):
        while self.is_running and self.remaining_time > 0:
            if not self.is_paused:
                mins, secs = divmod(self.remaining_time, 60)
                
                self.label.setText(f"{mins:02d}:{secs:02d}")  # Actualiza el QLabel
                print(f"Tiempo restante: {mins:02d}:{secs:02d}")

                time.sleep(1)
                self.remaining_time -= 1
        if self.remaining_time == 0:
            print("¡Tiempo terminado!")
        self.is_running = False

    def pausar_partido(self):
        if self.is_running:
            self.is_paused = True
            print("Cronómetro pausado")

    def reanudar_partido(self):
        if self.is_paused:
            self.is_paused = False
            print("Cronómetro reanudado")
    
    def detener_partido(self):
        self.is_running = False
        self.is_paused = False
        print("Cronómetro detenido")

    def reiniciar_partido(self, minutos=None, segundos=None):
        if minutos is not None and segundos is not None:
            self.total_time = minutos * 60 + segundos
        self.remaining_time = self.total_time
        self.is_paused = False
        print("Cronómetro reiniciado")
        self.iniciar_partido()



class Marcador:
    def __init__(self, equipo1, equipo2, label):
        self.equipo1 = equipo1
        self.equipo2 = equipo2

        self.marcador = [0, 0] #Locales - Visitantes
        self.label = label

    def anotar_gol(self, equipo):
        if equipo == 0:
            self.marcador[0] += 1 #Gol para locales
            print("Gol locales.")
        elif equipo == 1:
            self.marcador[1] += 1 #Gol para visitantes
            print("Gol visitantes.")
        else:
            print("Equipo no válido.")

        self.label.setText(f"{self.marcador[0]} - {self.marcador[1]}")



# Ejemplo de uso:
if __name__ == "__main__":

    # Ejemplo de uso
    cronometro = Cronometro(1, 30)  # Cuenta regresiva de 1 minuto y 30 segundos
    cronometro.iniciar_partido()

    # Pausar después de 3 segundos
    time.sleep(3)
    cronometro.pausar_partido()

    # Continuar después de 2 segundos
    time.sleep(2)
    cronometro.reanudar_partido()

    # Detener el cronómetro después de otros 5 segundos
    time.sleep(5)
    cronometro.detener_partido()

    # Reiniciar con un nuevo tiempo
    cronometro.reiniciar_partido(0, 10)  # 10 segundos de cuenta regresiva


    partido = Marcador("Barcelona", "Real Madrid")
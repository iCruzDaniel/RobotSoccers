import serial

class SerialConnection:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.connection.is_open:
                print(f"Conectado al puerto {self.port}")
        except serial.SerialException as e:
            print(f"No se pudo conectar al puerto {self.port}: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"Desconectado del puerto {self.port}")

    def send_data(self, data):
        if self.connection and self.connection.is_open:
            self.connection.write(data.encode())
            print(f"Datos enviados: {data}")

    def receive_data(self):
        if self.connection and self.connection.is_open:
            data = self.connection.readline().decode('utf-8').strip()
            print(f"Datos recibidos: {data}")
            return data

# Ejemplo de uso
if __name__ == "__main__":
    serial_obj = SerialConnection(port='COM3', baudrate=9600)
    serial_obj.connect()
    
    # Enviar datos
    serial_obj.send_data("Hola desde Python")

    # Recibir datos
    received = serial_obj.receive_data()
    
    # Desconectar
    serial_obj.disconnect()

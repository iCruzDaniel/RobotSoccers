import serial
import time
import sys 
import glob

def list_ports():
    """Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class SerialConnection:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)
        if self.connection.is_open:
            print(f"Conectado al puerto {self.port}")


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

    serial_obj = SerialConnection(port='COM8', baudrate=9600)
    #serial_obj.connect()

    # Llama a la función para obtener la lista de puertos
    ports = serial_obj.list_ports()
    print(ports)
    
    # Enviar datos
    """
    TRAMA DE EJMPLO: TA1110D7770|
    [T] --> Indica la transmición de datos
    [A] Primera letra --> Movimiento maquina 1
    [111] siguientes 3 Digitos --> PWM Motores maquina 1
    [0] Cuerto dígito despues de la última letra--> indicador de pateo maquina 1
    [D] Segunda letra --> Movimiento maquina 2
    [777] siguientes 3 Digitos --> PWM Motores maquina 2
    [0] Cuerto dígito despues de la última letra--> indicador de pateo maquina 2
    | --> Indicador de que se acabó la trama
    """
    serial_obj.send_data("TA1110D7770|") # Trama T

    # Recibir datos
    #received = serial_obj.receive_data()
    
    # Desconectar
    serial_obj.disconnect()

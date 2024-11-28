#include <AFMotor.h>  //Libreria Motores
AF_DCMotor Motor1(1);
AF_DCMotor Motor2(2);
AF_DCMotor Motor3(3);
AF_DCMotor Motor4(4);

#include <SoftwareSerial.h>
SoftwareSerial WMBT(A4, A5);  // RX, TX recorder que se cruzan
//SoftwareSerial WMBT(10, 11);  // RX, TX recorder que se cruzan


#include "VAR.h"
//MAQUINA
int M = MAQUINA_2;  //Cambiar este valor dependiendo de la maquina que se vaya a programar...

//Char recibido = 0;
String tramaRecibida;
//{movimiento_m1(1)|pwm_m1(3)|palanca_m1(1)|movimiento_m2(1)|pwm_m2(3)|palanca_m2(1)|'\n'} = tamaño14
// moviento->[0] | pwm/100->[1] pwm/10->[2] pwm->[3] | palanca->[4]

int vel = 0;           //Velocidad de los motores 0 - 255
char movimiento = "";  //Movimientos posibles: QWEASDZC
bool palanca = false;  // Servomotor

// ---- Funciones Complementarias ----
bool convertirCharABool(char caracter) {
  return caracter == 'V';
}

// ----- Funciones de los Motores ----
// Funciones de movimiento (sin cambios)
void adelante(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(FORWARD); 
  Motor2.setSpeed(vel);
  Motor2.run(FORWARD);
  Motor3.setSpeed(vel);
  Motor3.run(FORWARD);
  Motor4.setSpeed(vel);
  Motor4.run(FORWARD);
}

void retroceder(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(BACKWARD); 
  Motor2.setSpeed(vel);
  Motor2.run(BACKWARD);
  Motor3.setSpeed(vel);
  Motor3.run(BACKWARD);
  Motor4.setSpeed(vel);
  Motor4.run(BACKWARD);
}

void derecha(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(BACKWARD); 
  Motor2.setSpeed(vel);
  Motor2.run(FORWARD);
  Motor3.setSpeed(vel);
  Motor3.run(BACKWARD);
  Motor4.setSpeed(vel);
  Motor4.run(FORWARD);
}

void izquierda(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(FORWARD); 
  Motor2.setSpeed(vel);
  Motor2.run(BACKWARD);
  Motor3.setSpeed(vel);
  Motor3.run(FORWARD);
  Motor4.setSpeed(vel);
  Motor4.run(BACKWARD);
}
/*
void adelanteizquierda(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(BACKWARD);
  Motor2.setSpeed(vel);
  Motor2.run(BACKWARD);
  Motor3.setSpeed(vel);
  Motor3.run(FORWARD);
  Motor4.setSpeed(vel);
  Motor4.run(FORWARD);
}

void adelantederecha(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(FORWARD);
  Motor2.setSpeed(vel);
  Motor2.run(FORWARD);
  Motor3.setSpeed(vel);
  Motor3.run(BACKWARD);
  Motor4.setSpeed(vel);
  Motor4.run(BACKWARD);
}
*/
void diagonal1(int vel = 255) {
  Motor1.setSpeed(0);
  Motor1.run(RELEASE); 
  Motor2.setSpeed(vel);
  Motor2.run(BACKWARD);
  Motor3.setSpeed(0);
  Motor3.run(RELEASE);
  Motor4.setSpeed(vel);
  Motor4.run(BACKWARD);
}

void diagonal2(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(FORWARD); 
  Motor2.setSpeed(0);
  Motor2.run(RELEASE);
  Motor3.setSpeed(vel);
  Motor3.run(FORWARD);
  Motor4.setSpeed(0);
  Motor4.run(RELEASE);
}

void diagonal3(int vel = 255) {
  Motor1.setSpeed(0);
  Motor1.run(RELEASE); 
  Motor2.setSpeed(vel);
  Motor2.run(FORWARD);
  Motor3.setSpeed(0);
  Motor3.run(RELEASE);
  Motor4.setSpeed(vel);
  Motor4.run(FORWARD);
}

void diagonal4(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(BACKWARD); 
  Motor2.setSpeed(0);
  Motor2.run(RELEASE);
  Motor3.setSpeed(vel);
  Motor3.run(BACKWARD);
  Motor4.setSpeed(0);
  Motor4.run(RELEASE);
}

void giroHorario(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(FORWARD); 
  Motor2.setSpeed(vel);
  Motor2.run(FORWARD);
  Motor3.setSpeed(vel);
  Motor3.run(BACKWARD);
  Motor4.setSpeed(vel);
  Motor4.run(BACKWARD);
}

void giroAntihorario(int vel = 255) {
  Motor1.setSpeed(vel);
  Motor1.run(BACKWARD); 
  Motor2.setSpeed(vel);
  Motor2.run(BACKWARD);
  Motor3.setSpeed(vel);
  Motor3.run(FORWARD);
  Motor4.setSpeed(vel);
  Motor4.run(FORWARD);
}

void detener() {
  Motor1.setSpeed(0);
  Motor1.run(RELEASE);
  Motor2.setSpeed(0);
  Motor2.run(RELEASE);
  Motor3.setSpeed(0);
  Motor3.run(RELEASE);
  Motor4.setSpeed(0);
  Motor4.run(RELEASE);
}
unsigned long lastReceiveTime = 0;  // Tiempo de la última trama recibida
unsigned long timeout = 100;  // Tiempo máximo sin recibir una trama (en milisegundos)



// ----- MAIN ----
void setup() {
  WMBT.begin(9600);
  Serial.begin(9600);  // Comunicación con el monitor serial de la PC
  Motor1.run(RELEASE);
  Motor2.run(RELEASE);
  Motor3.run(RELEASE);
  Motor4.run(RELEASE);
  
}


void loop() {
/*
  // Limpiar el buffer antes de leer
  while (WMBT.available() > 0) {
    WMBT.read();
  }
  */

  // Enviar la trama desde tu programa principal
 //Serial.print("Hola, Arduino!");

  // Leer la trama completa en el Arduino
if (WMBT.available() > 0) {
   //WMBT.read();
  tramaRecibida = WMBT.readStringUntil('|');  // Leer hasta un salto de línea
  Serial.print("Comando recibido (trama completa): ");
  Serial.println(tramaRecibida);  // Imprime la trama completa en una sola línea
  if (tramaRecibida[0] == 'D') {

    movimiento = tramaRecibida[1 + M];
    vel = 100 * (tramaRecibida[M + 2] - '0') + 10 * (tramaRecibida[M + 3] - '0') + (tramaRecibida[M + 4] - '0');
    palanca = convertirCharABool(tramaRecibida[M + 5]);

    Serial.print("Trama separada: ");
    Serial.print(movimiento);
    Serial.print(" ");
    Serial.print(vel);
    Serial.print(" ");
    Serial.println(palanca);  //false == 0
   
   // Actualizamos el tiempo de la última trama recibida
    lastReceiveTime = millis();


    WMBT.flush();
    //WMBT.println("R");
  }
  else {
    WMBT.flush();
  }
}
 // Verificar si ha pasado mucho tiempo sin recibir trama
  if (millis() - lastReceiveTime > timeout) {
    detener();  // Detenemos los motores si no se recibe nada dentro del tiempo límite
  }


  /*int band = 0;
  while (WMBT.available()) {
    delay(50);
    char recibido = WMBT.read();
    WMBT.flush();
    tramaRecibida[band] = recibido;  // Acumula los caracteres en la trama
    // Si la trama ha terminado (por ejemplo, con un salto de línea '\n')
    if (recibido == '|') {
      Serial.print("Comando recibido (trama completa): ");
      Serial.println(tramaRecibida);  // Imprime la trama completa en una sola línea

      movimiento = tramaRecibida[0 + M];
      vel = 100 * (tramaRecibida[M + 1] - '0') + 10 * (tramaRecibida[M + 2] - '0') + (tramaRecibida[M + 3] - '0');
      palanca = convertirCharABool(tramaRecibida[M + 4]);

      Serial.print("Trama separada: ");
      Serial.print(movimiento);
      Serial.print(" ");
      Serial.print(vel);
      Serial.print(" ");
      Serial.println(palanca);  //false == 0

      //tramaRecibida.clear();             // Limpia la trama para la próxima recepción
      band = 0;
    }
    band += 1;
  }*/

  // Selección de movimientos
  switch (movimiento) {
    case 'W':
      adelante();
      //delay(100);
      WMBT.println("Adelante");
      break;
    case 'S':
      retroceder();
      WMBT.println("Reversa");
      break;
    case 'A':
      izquierda();
      WMBT.println("Izquierda");
      break;
    case 'D':
      derecha();
      WMBT.println("Derecha");
      break;
    case 'Z':
      diagonal1();
      WMBT.println("diagonal 1");
      break;
    case 'Q':
      diagonal2();
      WMBT.println("diagonal 2");
      break;
    case 'E':
      diagonal3();
      WMBT.println("diagonal 3");
      break;
    case 'C':
      diagonal4();
      WMBT.println("diagonal 4");
      break;
    case 'F':
      giroHorario();
      WMBT.println("giro Derecha");
      break;
    case 'X':
      giroAntihorario();
      WMBT.println("giro Izquierda");
      break;
    case 'P':
      detener();
      WMBT.println("Detener");
      break;
  }
  movimiento = ' ';
}

extern "C" {
  int main_validator(const char* inizio, const char* fine); 
  int controllo_dinamico_loop(const char* inizio, const char* fine);
}

#define MAX_BUFFER_SIZE 1000 
#define LED_PIN 8 
#define LED_LOOP_PIN 10

char inputBuffer[MAX_BUFFER_SIZE];
int bufferIndex = 0;

void setup() {
  Serial.setRxBufferSize(512); 
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_LOOP_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); 
  digitalWrite(LED_LOOP_PIN, HIGH); 
  Serial.println("Sistema pronto");
}


void trasmettiLoopMorse() {
  // L: .-..  O: ---  O: ---  P: .--.
  const char* morseLoop[] = {".-..", "---", "---", ".--."};
  int punto = 200; 
  int linea = 600; 

  for (int i = 0; i < 4; i++) {
    const char* simbolo = morseLoop[i];
    for (int j = 0; simbolo[j] != '\0'; j++) {
      digitalWrite(LED_LOOP_PIN, HIGH);
      delay(simbolo[j] == '.' ? punto : linea);
      digitalWrite(LED_LOOP_PIN, LOW);
      delay(punto); 
    }
    delay(linea); 
  }
}

void gestisciBlink(int n) {
  if (n <= 0) return;

  for (int i = 0; i < n; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(600);
    digitalWrite(LED_PIN, LOW);
    delay(600);
  }

  delay(2000);

  unsigned long startTime = millis();
  while (millis() - startTime < 5000) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
  Serial.println("controlli statici terminati con errore, identificare l'errore sul manuale.");
  Serial.println("RIAVVIA MANUALMENTE LA SCHEDA.");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (bufferIndex > 0) {
        inputBuffer[bufferIndex] = '\0';
        
        Serial.print("Ricevuti: ");
        Serial.print(bufferIndex);
        Serial.println(" caratteri.");

        /*Serial.println(inputBuffer);
        Serial.println(inputBuffer + bufferIndex);*/

        int res = main_validator(inputBuffer, inputBuffer + bufferIndex);

        /*Serial.println(inputBuffer);
        Serial.println(inputBuffer + bufferIndex);*/

        if (res == 0) {
          int res2 = controllo_dinamico_loop(inputBuffer, inputBuffer + bufferIndex);
          Serial.println("Controlli statici superati");
          Serial.println("RIAVVIA MANUALMENTE LA SCHEDA.");
          /*
          if (res2 == 0) {
            Serial.println("Codice funzionate");
            Serial.println("RIAVVIA MANUALMENTE LA SCHEDA.");
          }
          else {
            Serial.println("Errore dinamico rilevato: Segnalazione su LED 10");
            Serial.println("RIAVVIA MANUALMENTE LA SCHEDA.");
            trasmettiLoopMorse();
          }*/
        } else {
          gestisciBlink(res);
        }
        
        bufferIndex = 0;
      }
    } 
    else {
      if (bufferIndex < MAX_BUFFER_SIZE - 1) {
        inputBuffer[bufferIndex++] = c;
      }
    }
  }
  yield(); 
}
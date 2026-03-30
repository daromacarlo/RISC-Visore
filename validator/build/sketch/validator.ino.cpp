#include <Arduino.h>
#line 1 "C:\\Users\\Carlo Da Roma\\Documents\\Arduino\\validator\\validator.ino"
extern "C" {
  int controlli_statici(const char* inizio, const char* fine); 
  int controllo_dinamico_loop(const char* inizio, const char* fine);
  int riscvprg(); // Questa è la funzione definita nel tuo file .S
}

#define MAX_BUFFER_SIZE 1000 
#define LED_PIN 8 
#define LED_LOOP_PIN 10

char inputBuffer[MAX_BUFFER_SIZE];
int bufferIndex = 0;

#line 14 "C:\\Users\\Carlo Da Roma\\Documents\\Arduino\\validator\\validator.ino"
void setup();
#line 24 "C:\\Users\\Carlo Da Roma\\Documents\\Arduino\\validator\\validator.ino"
void trasmettiLoopMorse();
#line 41 "C:\\Users\\Carlo Da Roma\\Documents\\Arduino\\validator\\validator.ino"
void gestisciBlink(int n);
#line 61 "C:\\Users\\Carlo Da Roma\\Documents\\Arduino\\validator\\validator.ino"
void loop();
#line 14 "C:\\Users\\Carlo Da Roma\\Documents\\Arduino\\validator\\validator.ino"
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

        // 1. Esecuzione controlli statici
        int res = controlli_statici(inputBuffer, inputBuffer + bufferIndex);

        if (res == 0) {
          Serial.println("Controlli statici superati");
          
          // 2. Esecuzione controlli dinamici
          int res2 = controllo_dinamico_loop(inputBuffer, inputBuffer + bufferIndex);
          
          if (res2 == 0) {
            Serial.println("Codice funzionante. Avvio programma RISC-V...");
            
            // --- MODIFICA QUI: Chiamata al programma Assembly ---
            int risultatoRiscv = riscvprg(); 
            // ----------------------------------------------------
            
            Serial.print("Esecuzione completata. Risultato: ");
            Serial.println(risultatoRiscv);
            Serial.println("RIAVVIA MANUALMENTE LA SCHEDA.");
          }
          else {
            Serial.println("Errore dinamico rilevato: Segnalazione su LED 10");
            Serial.println("RIAVVIA MANUALMENTE LA SCHEDA.");
            trasmettiLoopMorse();
          } 
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

struct RiscvResult {
  int tempo;
  int led_pin;
};

extern "C" {
  int controlli_statici(const char* inizio, const char* fine);
  int controllo_dinamico_loop(const char* inizio, const char* fine);
  RiscvResult riscvprg();
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
  delay(1000);
  Serial.println("READY");
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
  Serial.println("controlli dinamici terminati con errore.");
  Serial.println("RIAVVIA MANUALMENTE LA SCHEDA O ATTENDERE IL RIAVVIO AUTOMATICO.");
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
  Serial.println("controlli statici terminati con errore.");
  Serial.println("RIAVVIA MANUALMENTE LA SCHEDA O ATTENDERE IL RIAVVIO AUTOMATICO.");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    // Accumulo caratteri finché non arrivo a fine riga o riempio il buffer
    if (c == '\n' || c == '\r') {
      if (bufferIndex > 0) {
        inputBuffer[bufferIndex] = '\0';

        bool isAsm = (strncmp(inputBuffer, "ASM:", 4) == 0);
        bool isHex = (strncmp(inputBuffer, "HEX:", 4) == 0);
        bool isAmu = (strncmp(inputBuffer, "AMU:", 4) == 0);
        bool isAnc = (strncmp(inputBuffer, "ANC:", 4) == 0);
        bool isTst = (strncmp(inputBuffer, "TST:", 4) == 0);

        char* dataStart = inputBuffer + 4;
        int dataLen = bufferIndex - 4;

        Serial.print("Ricevuti: ");
        Serial.print(dataLen);
        Serial.println(" byte di codice.");

        // MODALITÀ TST
        if (isTst) {
          Serial.println("modalità tst: test sequenziale LED");

          int testPins[] = {0,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21}; 
          int numPins = sizeof(testPins) / sizeof(testPins[0]);

          for (int i = 0; i < numPins; i++) {
            pinMode(testPins[i], OUTPUT);
            
            Serial.print("Accensione Pin: ");
            Serial.println(testPins[i]);
            
            digitalWrite(testPins[i], HIGH);
            delay(300);
            digitalWrite(testPins[i], LOW); 
            delay(100);
          }

          Serial.println("Test completato.");
          bufferIndex = 0; 
          return;
        }

        // MODALITÀ ANC
        if (isAnc) {
          Serial.println("modalità anc, Assembly no controlli");
          Serial.println("Esecuzione programma passato...");
          RiscvResult res3 = riscvprg();
          Serial.print("Tempo: ");
          Serial.print(res3.tempo);
          Serial.print(" ms, Pin ");
          Serial.print("Mask: ");
          Serial.println(res3.led_pin, BIN);
          const int mapPin[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21}; 

          if (res3.tempo > 0 && res3.led_pin > 0) {
              for (int i = 0; i < 13; i++) {
                  if (bitRead(res3.led_pin, i)) {
                      pinMode(mapPin[i], OUTPUT);
                      digitalWrite(mapPin[i], LOW);
                  }
              }
              delay(res3.tempo);
              for (int i = 0; i < 13; i++) {
                  if (bitRead(res3.led_pin, i)) {
                      digitalWrite(mapPin[i], HIGH);
                  }
              }
          }
          bufferIndex = 0; 
          return;
        }

        // MODALITÀ ASM
        if (isAsm) {
          int res = controlli_statici(dataStart, dataStart + dataLen);
          if (res == 0) {
            Serial.println("Controlli statici superati");
          } else {
            gestisciBlink(res);
            bufferIndex = 0;
            return;
          }
          int res2 = controllo_dinamico_loop(dataStart, dataStart + dataLen);
          if (res2 == 0) {
            Serial.println("Codice funzionante");
          }
          else {
            Serial.println("Errore dinamico rilevato.");
            trasmettiLoopMorse();
            bufferIndex = 0;
            return;
          }
          Serial.println("modalità asm");
          Serial.println("Esecuzione programma passato...");
          RiscvResult res3 = riscvprg();
          Serial.print("Tempo: ");
          Serial.print(res3.tempo);
          Serial.print(" ms, Pin ");
          Serial.print("Mask: ");
          Serial.println(res3.led_pin, BIN);
          const int mapPin[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21}; 

          if (res3.tempo > 0 && res3.led_pin > 0) {
              for (int i = 0; i < 13; i++) {
                  if (bitRead(res3.led_pin, i)) {
                      pinMode(mapPin[i], OUTPUT);
                      digitalWrite(mapPin[i], LOW);
                  }
              }
              delay(res3.tempo);
              for (int i = 0; i < 13; i++) {
                  if (bitRead(res3.led_pin, i)) {
                      digitalWrite(mapPin[i], HIGH);
                  }
              }
          }
          bufferIndex = 0;
          return;
        }

        // MODALITÀ HEX
        if (isHex) {
          int res = controlli_statici(dataStart, dataStart + dataLen);
          if (res == 0) {
            Serial.println("Controlli statici superati");
          } else {
            gestisciBlink(res);
            bufferIndex = 0;
            return;
          }
          int res2 = controllo_dinamico_loop(dataStart, dataStart + dataLen);
          if (res2 == 0) {
            Serial.println("Codice funzionante");
          } else {
            Serial.println("Errore dinamico rilevato.");
            trasmettiLoopMorse();
            bufferIndex = 0;
            return;
          }
          Serial.println("modalità hex");
          bufferIndex = 0;
          return;
        }

        // MODALITÀ AMU
        if (isAmu) {
          int res = controlli_statici(dataStart, dataStart + dataLen);
          if (res == 0) {
            Serial.println("Controlli statici superati");
          } else {
            gestisciBlink(res);
            bufferIndex = 0;
            return;
          }
          int res2 = controllo_dinamico_loop(dataStart, dataStart + dataLen);
          if (res2 == 0) {
            Serial.println("Codice funzionante");
          } else {
            Serial.println("Errore dinamico rilevato.");
            trasmettiLoopMorse();
            bufferIndex = 0;
            return;
          }
          Serial.println("modalità amu");
          Serial.println("Esecuzione programma passato...");
          RiscvResult res3 = riscvprg();
          Serial.print("Tempo: ");
          Serial.print(res3.tempo);
          Serial.print(" ms, Pin ");
          Serial.print("Mask: ");
          Serial.println(res3.led_pin, BIN);
          const int mapPin[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21}; 

          if (res3.tempo > 0 && res3.led_pin > 0) {
              for (int i = 0; i < 13; i++) {
                  if (bitRead(res3.led_pin, i)) {
                      pinMode(mapPin[i], OUTPUT);
                      digitalWrite(mapPin[i], LOW);
                  }
              }
              delay(res3.tempo);
              for (int i = 0; i < 13; i++) {
                  if (bitRead(res3.led_pin, i)) {
                      digitalWrite(mapPin[i], HIGH);
                  }
              }
          }
          bufferIndex = 0;
          return;
        }
        
        bufferIndex = 0;
      }
    } else {
      if (bufferIndex < MAX_BUFFER_SIZE - 1) {
        inputBuffer[bufferIndex++] = c;
      }
    }
  }
}
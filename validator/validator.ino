// Definiamo una struttura per contenere i due valori di ritorno
struct RiscvResult {
  int tempo;   // Tempo di accensione in millisecondi (x)
  int led_pin; // Numero del pin del LED (y)
};

extern "C" {
  int controlli_statici(const char* inizio, const char* fine); 
  int controllo_dinamico_loop(const char* inizio, const char* fine);
  
  // Modifichiamo la firma per restituire la struttura
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

        int res = controlli_statici(inputBuffer, inputBuffer + bufferIndex);

        if (res == 0) {
          Serial.println("Controlli statici superati");
          int res2 = controllo_dinamico_loop(inputBuffer, inputBuffer + bufferIndex);
          
          if (res2 == 0) {
            Serial.println("Codice funzionante");
            Serial.println("avvio codice.");
            
            // Chiamata alla funzione assembly che ritorna la struttura
          RiscvResult res3 = riscvprg();
            
            Serial.print("Tempo ricevuto: ");
            Serial.print(res3.tempo);
            Serial.print(" ms, LED scelto: Pin ");
            Serial.println(res3.led_pin);
            
            // Assicuriamoci che il tempo sia positivo e il pin sia valido
            if (res3.tempo > 0 && res3.led_pin >= 0) {
              // Impostiamo il pin ritornato da RISC-V come OUTPUT
              pinMode(res3.led_pin, OUTPUT); 
              
              // Accendiamo il led y per x tempo
              digitalWrite(res3.led_pin, LOW);
              delay(res3.tempo);
              digitalWrite(res3.led_pin, HIGH);
            }
          
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
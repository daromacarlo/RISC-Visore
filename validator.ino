extern "C" {
  void main_validator(const char* inizio, const char* fine); 
}

#define MAX_BUFFER_SIZE 1000 
char inputBuffer[MAX_BUFFER_SIZE];
int bufferIndex = 0;

void setup() {
 
  Serial.setRxBufferSize(512); 
  
  Serial.begin(115200);
  
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH); 

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

        main_validator(inputBuffer, inputBuffer + bufferIndex);
        
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
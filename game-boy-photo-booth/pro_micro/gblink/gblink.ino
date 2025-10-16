#include <SPI.h>
#include <avr/power.h>

#define BUFFERSIZE 1024

uint8_t sendBuffer[BUFFERSIZE];

int sendIndex = 0;
int writeIndex = 0;

void setup() {
  pinMode(MISO, INPUT_PULLUP);
  pinMode(MOSI, OUTPUT);
  pinMode(SCK, OUTPUT);

  clock_prescale_set(clock_div_4);
  Serial.begin(115200);
  SPI.begin();
  SPI.beginTransaction(SPISettings(32768, MSBFIRST, SPI_MODE3)); //This is the highest speed that worked in my test. Normal Game Boy speed would be around 8192.
}

void loop() {
  if (Serial.available() > 0) {
        sendBuffer[writeIndex++] = Serial.read();
        if (writeIndex == BUFFERSIZE)
            writeIndex = 0;
  }

  if (writeIndex != sendIndex) {
    uint8_t mosi = sendBuffer[sendIndex++];
    if (sendIndex == BUFFERSIZE)
        sendIndex = 0;
    uint8_t miso = SPI.transfer(mosi);
    Serial.write(miso);
  }
}

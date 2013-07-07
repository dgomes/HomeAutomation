/*
 * iRemotuino - Remote IR and RF Control for Sony TV and Chacon Ref:54656 
 * Diogo Gomes <diogogomes@gmail.com>
 * Copyright 2012
 */
//#define DEBUG

#include <IRremote.h> //http://github.com/shirriff/Arduino-IRremot
#include <RemoteTransmitter.h> //https://bitbucket.org/fuzzillogic/433mhzforarduino

IRsend irsend;

#define IRLED_PIN 3
#define RF_RECEIVER_PIN 2  
#define RF_TRANSMITTER_PIN 9
#define LM35sensorPin 0  //A0
#define RF_PERIOD 480 //usecs (as detected for Chacon Ref:54656 using a 434mhz receiver and fuzzillogic example code)

#define SONY 'S'
#define RC5 'Z' //used by ZonBox (Thomson model at least)
#define RF 'R'

void setup()
{
  pinMode(IRLED_PIN, OUTPUT);     
  pinMode(RF_TRANSMITTER_PIN, OUTPUT);     
  pinMode(RF_RECEIVER_PIN, INPUT);
  digitalWrite(RF_RECEIVER_PIN, HIGH); //pull up
  
  Serial.begin(115200);
  Serial.println("Home Automation v0");
}

float lm35temperature() {
  //getting the voltage reading from the temperature sensor
  int reading = analogRead(LM35sensorPin);  

  //http://playground.arduino.cc/Main/LM35HigherResolution 
  return reading*0.45;
}

void handlePacket(unsigned long packet) {
  byte humidity;
  humidity = packet & 0xFF;
  
  word temp;
  float temperature = 0;
  temp = (packet >> 8) & 0x7FFF;
  if( (packet >> 8) & 0x8000)
    temperature = float(temp)/10;
  else
    temperature = -1.0 * float(temp)/10;

  #ifdef DEBUG
  Serial.print(String("{\"code\": 101, \"Humidity\": ")+humidity); 
  Serial.print(String(", \"OutdoorTemperature\": ")); 
  Serial.print(float(temperature));
  Serial.print(String(", \"IndoorTemperature\": "));
  Serial.print(lm35temperature());
  Serial.println(String("}"));
  #endif

  //Specs http://www.amazon.co.uk/gp/product/B00327G0MA/ref=oh_details_o00_s00_i00
  if(humidity < 0 || humidity > 100) {//sanity check according to specs
    #ifdef DEBUG
    Serial.print("{\"code\": 303, \"error\": \"Invalid Humidity \"}");
    #endif
    return;
  }
  if(temperature < -20.0 || temperature>50.0) { //sanity check according to specs 
    #ifdef DEBUG
    Serial.print("{\"code\": 304, \"error\": \"Invalid Temperature ");
    Serial.print(temperature);
    Serial.println("\"}");
    #endif
    return;
  }
  Serial.print(String("{\"code\": 100, \"Humidity\": ")+humidity); 
  Serial.print(String(", \"OutdoorTemperature\": "));
  Serial.print(temperature);
  Serial.print(String(", \"IndoorTemperature\": "));
  Serial.print(lm35temperature());
  Serial.println(String("}"));
}


int rfdecode()
{
  static unsigned long packetInt;
  static unsigned bitsread;
  unsigned long time, t;

  t = pulseIn(RF_RECEIVER_PIN, LOW, 20000);
  //recover interrupted bits
  if(time < 1000)
    time += t;
  else
    time = t;

  if(time == 0) {
    bitsread = 0; //reset packet
    packetInt = 0;
    return 0;
  }
  if(time > 6000) {
    #ifdef DEBUG
    if(bitsread)
	Serial.println(String("{\"code\": 305, \"error\": \"bitsread " + String(bitsread) + "\"}"));
    #endif
    if(bitsread >= 32 && bitsread <=37)
      handlePacket(packetInt);
    bitsread = 0;
  } if(time > 1000 && time < 3000) { //bit 0
    bitsread++;
    packetInt = packetInt << 1;
    bitClear(packetInt, 0);

  } if(time > 3000 && time < 6000) { //bit 1
    bitsread++;
    packetInt = packetInt << 1;
    bitSet(packetInt, 0);
  }
  return 1;
}

unsigned long readCode() {
  
  // Read 8 hex characters
  if (Serial.available() < 8) return 0;
    
  unsigned long code = 0;
  for (int i = 0; i < 8; i++) {
    char ch = Serial.read();
    code = code << 4; //make way for new char
    if (ch >= '0' && ch <= '9') {
      code += ch - '0';
    } else if (ch >= 'a' && ch <= 'f') {
      code += ch - 'a' + 10;
    } else if (ch >= 'A' & ch <= 'F') {
      code += ch - 'A' + 10;
    } else {
      Serial.print("{\"code\": 301, \"error\": \"Unexpected hex char ");
      Serial.print(ch);
      Serial.println("}");
      Serial.flush();
      return 0;
    }
  }
  return code; 
}

void sendIRCommand(char type, int code) {
  switch(type) {
    case SONY:
      for (int i = 0; i < 6; i++) {
        digitalWrite(IRLED_PIN, HIGH);   // set the LED on
        irsend.sendSony(code, 12); // Sony TV code
        delay(100);
        digitalWrite(IRLED_PIN, LOW);   // set the LED off
      }
      break;
    case RC5:
        digitalWrite(IRLED_PIN, HIGH);   // set the LED on
        irsend.sendRC5(code, 12);
        delay(100);
        digitalWrite(IRLED_PIN, LOW);   // set the LED off
      break;
  } 
}

void loop() {
  while(rfdecode()) {Serial.print("");};
  
  if (Serial.available() < 9) {
    return;
  }
  char type = Serial.read();
  //Reads the extra 8 chars
  unsigned long code = readCode();
  /* Debug
  Serial.print("0x");
  Serial.println(code, HEX);
  */
  switch(type) {
    case SONY:
    case RC5:
      sendIRCommand(type, code);
      break;
    case RF:
      // Retransmit the signal 8 times ( == 2^3) on pin RF_TRANSMITTER. Note: no object was created!
      RemoteTransmitter::sendCode(RF_TRANSMITTER_PIN, code, RF_PERIOD, 3);
      break;
    default:
      Serial.print("{\"code\": 302, \"error\": \"Unexpected type ");
      Serial.print(type);
      Serial.print("\"}");
    }
  Serial.println("{\"code\": 200}");
  Serial.flush();
}


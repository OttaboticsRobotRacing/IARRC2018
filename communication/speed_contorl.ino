/**
 * Divides a given PWM pin frequency by a divisor.
 * 
 * The resulting frequency is equal to the base frequency divided by
 * the given divisor:
 *   - Base frequencies:
 *      o The base frequency for pins 3, 9, 10, and 11 is 31250 Hz.
 *      o The base frequency for pins 5 and 6 is 62500 Hz.
 *   - Divisors:
 *      o The divisors available on pins 5, 6, 9 and 10 are: 1, 8, 64,
 *        256, and 1024.
 *      o The divisors available on pins 3 and 11 are: 1, 8, 32, 64,
 *        128, 256, and 1024.
 * 
 * PWM frequencies are tied together in pairs of pins. If one in a
 * pair is changed, the other is also changed to match:
 *   - Pins 5 and 6 are paired on timer0
 *   - Pins 9 and 10 are paired on timer1
 *   - Pins 3 and 11 are paired on timer2
 * 
 * Note that this function will have side effects on anything else
 * that uses timers:
 *   - Changes on pins 3, 5, 6, or 11 may cause the delay() and
 *     millis() functions to stop working. Other timing-related
 *     functions may also be affected.
 *   - Changes on pins 9 or 10 will cause the Servo library to function
 *     incorrectly.
 * 
 * Thanks to macegr of the Arduino forums for his documentation of the
 * PWM frequency divisors. His post can be viewed at:
 *   http://forum.arduino.cc/index.php?topic=16612#msg121031
 */
const int CH1 = 9;
//const int CH2 = 10;

int spd = 0;
String inString = "";


void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 32: mode = 0x03; break;
      case 64: mode = 0x04; break;
      case 128: mode = 0x05; break;
      case 256: mode = 0x06; break;
      case 1024: mode = 0x07; break;
      default: return;
    }
    TCCR2B = TCCR2B & 0b11111000 | mode;
  }
}

void setup() {
  setPwmFrequency(CH1, 64);     // CH1: Stearing
  //setPwmFrequency(CH2, 256);     // CH2: Speed Control
  Serial.begin(9600);
  pinMode(10, INPUT);
  pinMode(11, INPUT);
  pinMode(8, OUTPUT);
  //delay(1000);
}

void loop() {
  digitalWrite(8,HIGH);
  if(Serial.available() > 0){
    int inChar =Serial.read();
    if (isDigit(inChar)) {
      // convert the incoming byte to a char and add it to the string:
      inString += (char)inChar;
    }
    if (inChar == '\n') {
      Serial.print("Value:");
      Serial.println((inString.toInt()));
      spd=inString.toInt();
      // clear the string for new input:
      inString = "";
    }
  }
  analogWrite (CH1, spd);  // Speed
 // Fault returns
  if (digitalRead(10) == HIGH && digitalRead(11) == HIGH)
{
  Serial.println("High High");//"Under Voltage");
}
else if (digitalRead(10) == HIGH && digitalRead(11) == LOW)
{
  Serial.println("High LOW");//"Over Temperature, Overheating Warning");
}
else if (digitalRead(10) == LOW && digitalRead(11) == HIGH)
{
  Serial.println ("LOW HIGH");//"Short Circuit");
}

else if(digitalRead(10) == LOW && digitalRead(11) == LOW)
{
  Serial.println ("LOW LOW");//"No fault");
}
delay(500);
  // Servo is just CH2
  //analogWrite (CH1, 60); delay(7000);         // Angle
  //analogWrite (CH1, 32); delay(2000);       // Left    @1ms  
  //analogWrite(CH1, 50);  delay(2000);       // Neutral @1.615ms
  //analogWrite(CH1, 62);  delay(2000);       // Right   @1.975ms
  
  //analogWrite (CH2, 32); delay(2000);       // Back    @1ms
  //analogWrite(CH2, 47);  delay(2000);       // Neutral @1.5ms
  //analogWrite(CH2, 65);  delay(2000);       // Forward @2ms
}

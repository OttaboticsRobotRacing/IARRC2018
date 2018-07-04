/*
Arduino Master

- process serial commands from computer
- set car steering angle and speed
- requests fault pin status from Arduino Slave 0
- checks for estop interrupt from Arduino Slave 0

*/

#include <Wire.h>
#include <Servo.h>

// servo and speed controller pins
const int STEERING_PIN = 9;
const int SPEED_PIN = 5;

const int ESC_DIRECTION_PIN = 8;
const int ESC_RESET_PIN = 7;

// fault flags
const int FAULT_PIN_0 = 3;
const int FAULT_PIN_1 = 4;

// servo and speed controller default states
volatile int angle = 90;
volatile int speed = 0;

// interrupt pins
const int ESTOP_PIN = 2; // 2 and 3 are the only interrupt pins

// String buffer max size
const int MAX_SIZE = 5;

// heartbeat setup
unsigned long prev_time;

const int LED_DELAY = 5;

volatile bool estop_triggered = false;

const int I2C_SLAVE_0_MESSAGE_SIZE = 2;

Servo steering_servo;

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
void setPwmFrequency(int pin, int divisor) {
    byte mode;
    if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
        switch(divisor)
        {
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

void estop_interrupt()
{
    speed = 0;
    angle = 0;
    //setSpeed(speed);
    //setAngle(angle);

    estop_triggered = true;

}

void setup()
{
    Serial.begin(9600);
    pinMode(LED_BUILTIN, OUTPUT);

    steering_servo.attach(STEERING_PIN);
    pinMode(SPEED_PIN, OUTPUT);

    pinMode(ESTOP_PIN, INPUT);
    attachInterrupt(0, estop_interrupt, LOW);

    pinMode(FAULT_PIN_0, INPUT);
    pinMode(FAULT_PIN_1, INPUT);

    pinMode(ESC_DIRECTION_PIN, OUTPUT);

    Wire.begin();

    prev_time = millis();

    delay(100);
}

void setAngle(int a)
{
    // 90 is straight
    // 60 left
    // 130 right
    angle = a;
    steering_servo.write(angle);
    Serial.print("A:");
    Serial.println(angle);
}

void setSpeed(int s)
{
    speed = s;
    analogWrite(SPEED_PIN, speed);
    Serial.print("S:");
    Serial.println(speed);
}

// insert interrupt function here

void check_fault_pins()
{

    if (digitalRead(FAULT_PIN_0) == HIGH && digitalRead(FAULT_PIN_1) == HIGH)
    {
        Serial.println("High High - Under voltage");
    }
    else if (digitalRead(FAULT_PIN_0) == HIGH && digitalRead(FAULT_PIN_1) == LOW)
    {
        Serial.println("High LOW - Over temperature, overheating warning");
    }
    else if (digitalRead(FAULT_PIN_0) == LOW && digitalRead(FAULT_PIN_1) == HIGH)
    {
        Serial.println ("LOW HIGH - Short circuit");
    }
    else if(digitalRead(FAULT_PIN_0) == LOW && digitalRead(FAULT_PIN_1) == LOW)
    {
        Serial.println ("LOW LOW - No fault");
    }
}

void processInput(String b)
{
    /*
    possible inputs:

    a### : set angle
    v### : set speed

    */

    if (b.length() >= 1 && b.length() <= 4)
    {
        int value = 0;

        if (b.length() == 1)
        {
            if (b[0] == 'r')
            {
                estop_triggered = false;
                Serial.println("R");
            }
            else
            {
                Serial.println("E:" + b);
            }
            return;
        }
        else if (b.length() == 2)
        {
            // set mode
            if (b[0] == 'm')
            {
                if (b[1] == 'a')
                {
                    // autonomous
                    Serial.println("M:auto");
                    return;
                }
                else if (b[1] == 'm')
                {
                    // manual mode
                    Serial.println("M:man");
                    return;
                }
            }
            else if (b[0] == 'a' || b[0] == 's')
            {
                char tmp[1];
                tmp[0] = b[1];
                value = atoi(tmp);
            }
            else if (b == "ff")
            {
                Serial.println("Getting fault flag");
                String ff_message = get_fault_pin_status();
                Serial.println("F:" + ff_message);
                return;
            }
            else
            {
                Serial.println("E:" + b + '-');
            }
        }
        else if (b.length() == 3)
        {
            char tmp[2];
            tmp[0] = b[1];
            tmp[1] = b[2];
            value = atoi(tmp);
        }
        else if (b.length() == 4)
        {
            char tmp[3];
            tmp[0] = b[1];
            tmp[1] = b[2];
            tmp[2] = b[3];
            value = atoi(tmp);
        }

        if (b[0] == 'a')
        {
            setAngle(value);
        }
        else if (b[0] == 's')
        {
            setSpeed(value);
        }
        else
        {
             Serial.println("E:" + b + '-');
        }

    }
    else if (b != "")
    {
        Serial.println("E:" + b + '-');
    }
}

String readSerialString()
{
    String s = "";
    int incomingByte = 0;
    char buffer[MAX_SIZE];
    int count = 0;

    if (Serial.available() > 0)
    {
        while (Serial.available())
        {
            incomingByte = Serial.read();
            delay(5);

            // reset buffer if its size reaches the max size for the array
            if (count >= MAX_SIZE - 1)
            {
                count = 0;
                memset(&buffer[0], 0, sizeof(buffer));
                Serial.println("E:len");
                return "";
            }

            // add one char at a time to char array buffer
            buffer[count] = char(incomingByte);
            count++;
        }
        buffer[count] = '\0';

        s = String(buffer);

        // reset buffer
        memset(&buffer[0], 0, sizeof(buffer));
        count = 0;
    }

    return s;
}

String get_fault_pin_status()
{
    String message = "";
    Wire.requestFrom(0, I2C_SLAVE_0_MESSAGE_SIZE);

    while (Wire.available())
    {
        char c = Wire.read();
        message += c;
    }

    return message;
}

void send_heartbeat()
{
    // send heartbeat every 3 seconds
    if (millis() - prev_time >= 3000)
    {
        Serial.print("HB:");
        Serial.println(millis() / 1000);
        prev_time = millis();
    }
}

void loop()
{
    while (estop_triggered)
    {
        Serial.println("STOP");
        if (readSerialString() == "r")
        {
            Serial.println("RESET");
            estop_triggered = false;
        }
        delay(1000);
    }

    String inputString = readSerialString();

    processInput(inputString);

    digitalWrite(ESC_DIRECTION_PIN, HIGH);
    setAngle(angle);
    setSpeed(speed);



    // do stuff here




    check_fault_pins();



    if (estop_triggered)
    {
        digitalWrite(LED_BUILTIN, HIGH);
    }
    else
    {
        digitalWrite(LED_BUILTIN, LOW);
    }

    send_heartbeat();
}

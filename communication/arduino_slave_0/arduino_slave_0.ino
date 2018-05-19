/*
Arduino slave 0

- read fault pins
- read RC receiver for wireless estop

*/

#include <Wire.h>

const int RC_TRIGGER_PIN = 10;
const int RC_KNOB_PIN = 9;
const int OUTPUT_INTERRUPT_PIN = 6;

const int FAULT_PIN_0 = 3;
const int FAULT_PIN_1 = 4;

const int I2C_DEVICE_ID = 0;

String fault_pin_status_message = "OK";

void setup()
{
    Wire.begin(I2C_DEVICE_ID);
    Wire.onRequest(requestEvent);

    pinMode(RC_KNOB_PIN, INPUT);
    pinMode(RC_TRIGGER_PIN, INPUT);
    pinMode(OUTPUT_INTERRUPT_PIN, OUTPUT);

    pinMode(LED_BUILTIN, OUTPUT);

    digitalWrite(OUTPUT_INTERRUPT_PIN, LOW);
    Serial.begin(9600);

    delay(3000);
}

void requestEvent()
{
    Wire.write(fault_pin_status_message);
}

void check_rc()
{
    /*
    Check status of RC receiver

    - if trigger is released or power is lost, set interrupt pin to HIGH
    - if knob is twisted, reset interrupt pin to LOW

    */

    int pwm_trig = pulseIn(RC_TRIGGER_PIN, HIGH, 20000); //Channel 2
    int pwm_knob = pulseIn(RC_KNOB_PIN, HIGH, 20000); //Channel 1

    Serial.print("pwm_trig ");
    Serial.println(pwm_trig);
    Serial.print("pwm_knob ");
    Serial.println(pwm_knob);

    if (pwm_trig <= 953 || pwm_trig >= 1113)
    {
        // +/-30 of 983 which is the pwm value when trigger is pressed. The trigger is pressed to run the car.
        digitalWrite(OUTPUT_INTERRUPT_PIN, HIGH);
        digitalWrite(LED_BUILTIN, HIGH);
    }

    if (pwm_knob <= 2008 && pwm_knob >= 1948)
    {
        // +/-30 of 1978 which is the pwm value when knob is turned clockwise.Twisting the knob will
        digitalWrite(OUTPUT_INTERRUPT_PIN, LOW);
        digitalWrite(LED_BUILTIN, LOW);
    }
}

void check_fault_pins()
{
    /*
    Read fault pins of the speed controller board

    - modify value of fault_pin_status_message to current state of fault pins
        - default value is "OK"

    */
    if (digitalRead(FAULT_PIN_0) == HIGH && digitalRead(FAULT_PIN_1) == HIGH)
    {
        fault_pin_status_message = "Under voltage";
        Serial.println("High High - Under voltage");
    }
    else if (digitalRead(FAULT_PIN_0) == HIGH && digitalRead(FAULT_PIN_1) == LOW)
    {
        fault_pin_status_message = "Over temperature";
        Serial.println("High LOW - Over temperature, overheating warning");
    }
    else if (digitalRead(FAULT_PIN_0) == LOW && digitalRead(FAULT_PIN_1) == HIGH)
    {
        fault_pin_status_message = "Short circuit";
        Serial.println ("LOW HIGH - Short circuit");
    }
    else if(digitalRead(FAULT_PIN_0) == LOW && digitalRead(FAULT_PIN_1) == LOW)
    {
        fault_pin_status_message = "OK";
        Serial.println ("LOW LOW - No fault");
    }
}

void loop()
{
    check_rc();
    check_fault_pins();
}

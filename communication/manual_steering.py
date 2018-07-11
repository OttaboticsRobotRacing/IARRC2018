import serial_communication
from curtsies import Input
import logging

MAX_LEFT = 60
MAX_RIGHT = 120

def write_serial_interactive():
    speed = 0
    angle = 90
    with Input(keynames='curses') as input_generator:
        for e in input_generator:
            message = ''

            if e == 'w':
                message = 's30'
            if e == 'a':
                if angle >= MAX_LEFT:
                    angle -= 10
                message = 'a' + str(angle)
            if e == 's':
                message = 's0'
            if e == 'd':
                if angle <= MAX_RIGHT:
                    angle += 10
                message = 'a' + str(angle)
            if e == 'r':
                message = 'r'

            if message != '':
                serial_communication.write_serial_message(message)
                print(message)
                print('\r')


            if e == 'q':
                return


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    write_serial_interactive()

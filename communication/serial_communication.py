import serial
import time
import threading
import queue
from curtsies import Input # pip3 install curtsies
from . import serial_constants
import logging

def read_serial_thread(q):
    connected = False

    try:
        ser = serial.Serial(serial_constants.SERIAL_PORT, serial_constants.BAUD_RATE, timeout=0)

        while not connected:
            connected = True

            while ser.isOpen():
                if (ser.inWaiting() > 0):
                    data_str = ser.read(ser.inWaiting()).decode('ascii')
                    print(data_str, end='')
                stay_alive = True
                if not q.empty():
                    stay_alive = q.get()
                if not stay_alive:
                    return
            print('end')
    except serial.serialutil.SerialException:
        print('Serial port not found')
        return

def read_serial():
    connected = False

    try:
        ser = serial.Serial(serial_constants.SERIAL_PORT, serial_constants.BAUD_RATE, timeout=0)

        while not connected:
            connected = True

            while ser.isOpen():
                if (ser.inWaiting() > 0):
                    data_str = ser.read(ser.inWaiting()).decode('ascii')
                    #print(data_str)
                    return data_str.replace('\n', '').replace('\r','')
            #print('end')
    except serial.serialutil.SerialException:
        print('Serial port not found')
        return

def write_serial_message(message):
    message = message.encode('ascii')
    logging.debug('writing message: %s' % message)

    try:
        ser = serial.Serial(serial_constants.SERIAL_PORT, serial_constants.BAUD_RATE, timeout=0)
    except serial.serialutil.SerialException:
        logging.debug('Serial port not found')
        return

    ser.close()
    ser.open()

    ser.write(message)

    ser.close()


def write_serial_interactive():
    with Input(keynames='curses') as input_generator:
        for e in input_generator:
            message = ''

            if e == 'w':
                message = 'w'
            if e == 'a':
                message = 'a'
            if e == 's':
                message = 's'
            if e == 'd':
                message = 'd'

            if message != '':
                write_serial_message(message)
                print('\r')


            if e == 'q':
                return

def start_reader_thread():
    q = queue.Queue()

    reader = threading.Thread(target=read_serial_thread, args=(q,))
    reader.start()

    return reader, q

def stop_reader_thread(q):
    q.put(False)

def main():
    pass

if __name__ == '__main__':
    main()

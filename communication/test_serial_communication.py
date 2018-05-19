import time
import serial_communication

NUM_ATTEMPTS = 5

def test(command, expected):
    print('Testing: %s -> %s' % (command, expected))
    serial_communication.write_serial_message(command)
    for i in range(NUM_ATTEMPTS):
        result = serial_communication.read_serial()
        print('\tAttempt %d: %s' % (i, result), end='')
        if result == expected:
            print('\r\t\t\t\t\t\tPASS')
            return
        else:
            print()
    print('\r\t\t\t\t\t\tFAIL')

def main():
    serial_communication.write_serial_message('')

    for i in range(3, 0, -1):
        print('\r' + str(i), end='')
        time.sleep(1)
    print('\r', end='')

    test('a1', 'A:1')
    test('a12', 'A:12')
    test('a123', 'A:123')

    test('s1', 'S:1')
    test('s12', 'S:12')
    test('s123', 'S:123')

    test('mm', 'M:man')
    test('ma', 'M:auto')

    test('t', 'E:t-')
    test('12345', 'E:len')
    test('1', 'E:1-')
    test('m', 'E:m-')
    test('mq', 'E:mq-')

    for i in range(16):
        test('a123', 'A:123')

if __name__ == '__main__':
    main()

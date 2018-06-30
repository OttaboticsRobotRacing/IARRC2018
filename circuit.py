import cv2
import numpy as np
import communication
import pathfinding.strategypid.pathfinding as pathfinder
import logging
import communication.serial_communication as comm

#logging.basicConfig(level=logging.DEBUG)
cap = cv2.VideoCapture(1)


# TODO: check for traffic light
# TODO: check traffic light colour


#reader, q = comm.start_reader_thread()

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        turn_angle = pathfinder.compute_turn_angle(grey)
        print('turn angle:', turn_angle)

        turn_angle_message = str('a%d' % int(turn_angle))
        comm.write_serial_message(turn_angle_message)
        comm.write_serial_message('s50')

        cv2.imshow('frame', frame)

        # TODO: check for finish line

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

#comm.stop_reader_thread(q)

cap.release()
cv2.destroyAllWindows()

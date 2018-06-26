import pathfinding
import cv2
import logging
import numpy as np
import queue

def get_line_segments(image):
    """
    Find the line segments in the frame using HoughLinesP
    :return:
    """

    image = cv2.GaussianBlur(image, (5, 5), 0)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    image = cv2.GaussianBlur(image, (5, 5), 0)

    mask_edges = cv2.Canny(image, 50, 100, apertureSize=3)

    # variables for HoughLinesP

    # max_line_gap = 20 # default/previous/initial value
    max_line_gap = 20
    min_line_length = 5
    threshold = 1

    lines = cv2.HoughLinesP(mask_edges, 1, np.pi/180, threshold, min_line_length, max_line_gap)

    try:
        for x1, y1, x2, y2 in lines[0]:
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    except:
        pass

    return image


logging.basicConfig(level=logging.DEBUG)

cap = cv2.VideoCapture('footage/copy_edit.avi')

q = queue.Queue(maxsize=5)

while cap.isOpened():
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cropped = gray[150:, :]

    angle = pathfinding.compute_turn_angle(cropped)
    print('Output turn angle: %s' % angle)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(gray, str(int(angle)), (10,300), font, 4, (0,255,0), 2, cv2.LINE_AA)
    # cv2.imshow('gray', gray)

    try:
        q.put(angle, block=False)
    except queue.Full:
        q.get()
        q.put(angle, block=False)

    sum = 0
    for e in list(q.queue):
        print('q:', e)
        sum += e

    print('avg angle:', sum/5)
    cv2.putText(gray, str(int(sum/5)), (10,300), font, 4, (0,255,0), 2, cv2.LINE_AA)
    cv2.imshow('gray', gray)

    '''
    cropped = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)
    line_img = get_line_segments(cropped)
    cv2.imshow('lines', line_img)
    '''


    #cv2.imshow('cropped', cropped)


    if cv2.waitKey(100) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

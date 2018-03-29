'''
vision module utility functions
'''
import sys
sys.path.append('../')

import cv2
import numpy as np


def resize_image(img, height):
    '''
    Resizes an image to the specified height
    :param img:
    :param height:
    :return:
    '''
    ratio = float(height) / img.shape[0]
    dim = (int(img.shape[1]*ratio), height)

    image = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return image

def get_roi(img, points):
    '''
    Returns image after being cropped to coordinates defined by the list points
    :param img:
    :param points:
    :return:
    '''
    x_list = []
    y_list = []
    for i in range(0, len(points), 2):
        x_list.append(points[i])
    for i in range(1, len(points), 2):
        y_list.append(points[i])

    tl = (min(x_list), min(y_list))
    br = (max(x_list), max(y_list))

    roi = img[tl[1]:br[1], tl[0]:br[0]]

    # print("top left coords: " + str(tl))
    # print("bottom right coords: " + str(br))

    return roi

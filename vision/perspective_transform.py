'''
vision module perspective_transform functions
'''
import sys
sys.path.append('../')
import cv2
import numpy as np

# paper dimensions in inches
PAPER_DIMENSIION_HEIGHT = 11
PAPER_DIMENSION_WIDTH = 8.5

PERSPECTIVE_TRANSFORM_SCALE_FACTOR = 12

def four_point_transform(pts=None):
    '''
    POC for perspective transform

    :param pts: float32 numpy array of size 4 containing the TL, TR, BL, BR points
    :return:
    '''
    final_top_left = (60, 155)
    final_top_right = (155, 60)
    final_bottom_left = (325, 420)
    final_bottom_right = (420, 325)

    if pts is None:
        pts = np.array([final_top_left,
                        final_top_right,
                        final_bottom_right,
                        final_bottom_left],
                    dtype="float32")

    max_width, max_height = 450, 450
    hwratio = 11 / 8.5  # letter size paper
    scale = int(max_width / 12)

    # center_x = 150
    center_x = int(max_width / 2)
    # center_y = 250
    center_y = int(max_height * 2/3)

    dst = np.array([
        [center_x - scale, center_y - scale * hwratio],  # top left
        [center_x + scale, center_y - scale * hwratio],  # top right
        [center_x + scale, center_y + scale * hwratio],  # bottom right
        [center_x - scale, center_y + scale * hwratio],  # bottom left
    ], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(pts, dst)

    return M


def apply_perspective_transformation(image):
    '''
    :param image: input image
    :return: image after perspective transform is applied
    '''
    final_top_left = (228, 170)
    final_top_right = (500, 210)
    final_bottom_left = (225, 325)
    final_bottom_right = (515, 325)

    pts = np.array([final_top_left,
                    final_top_right,
                    final_bottom_right,
                    final_bottom_left],
                   dtype="float32")

    max_height = image.shape[0]
    max_width = image.shape[1]
    hwratio = PAPER_DIMENSIION_HEIGHT / PAPER_DIMENSION_WIDTH  # letter size paper
    scale = int(max_width / PERSPECTIVE_TRANSFORM_SCALE_FACTOR)

    center_x = int(max_width / 2)
    center_y = int(max_height * 2 / 3)

    dst = np.array([
        [center_x - scale, center_y - scale * hwratio],  # top left
        [center_x + scale, center_y - scale * hwratio],  # top right
        [center_x + scale, center_y + scale * hwratio],  # bottom right
        [center_x - scale, center_y + scale * hwratio],  # bottom left
    ], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(pts, dst)

    try:
        output = cv2.warpPerspective(image, M, (max_width, max_height))
        return output
    except:
        return image

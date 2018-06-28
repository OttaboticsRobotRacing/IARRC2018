import cv2
from . import constants
import numpy as np


def apply_preprocessing(image):
    """
    Apply suite of basic image processing filters like blur and colour conversion
    :param image:
    :return:
    """
    # convert colour space from BGR to grey to BGR
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    # resize the image to height 480
    image = resize_image(image, constants.IMAGE_HEIGHT)
    # apply gaussian blur
    image = cv2.GaussianBlur(image, (3, 3), 0)

    return image


def write_to_log(message, log_file="LOG.txt"):
    with open(log_file, "a") as f:
        f.write(message)


def save_image(image, file_name):
    cv2.imwrite("SavedImages/" + file_name, image)


def record_video():
    pass


def apply_perspective_transformation_old(image):
    height = image.shape[0]
    width = image.shape[1]

    final_top_left = [60, 155]
    final_top_right = [155, 60]
    final_bottom_left = [325, 420]
    final_bottom_right = [420, 325]

    if constants.DEBUG_MESSAGES:
        print("DEBUG:: Utility.apply_perspective_transformation()")
        print("DEBUG:: height = %s" % height)
        print("DEBUG:: width = %s" % width)

        pts = np.array([tuple(final_top_left),
                        tuple(final_top_right),
                        tuple(final_bottom_right),
                        tuple(final_bottom_left)], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 255))

        cv2.putText(image, "TL", tuple(final_top_left), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))
        cv2.putText(image, "TR", tuple(final_top_right), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))
        cv2.putText(image, "BL", tuple(final_bottom_left), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))
        cv2.putText(image, "BR", tuple(final_bottom_right), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))

        cv2.imshow("DEBUG-apply_perspective_transformation", image)

    # [top-left], [top-right], [bottom-left], [bottom-right]
    final_pts = np.float32([[0, 0],
                            [width - 1, 0],
                            [0, height - 1],
                            [width - 1, height - 1]])
    image_pts = np.float32([final_top_left,
                            final_top_right,
                            final_bottom_left,
                            final_bottom_right])

    try:
        M = cv2.perspectiveTransform(image_pts, final_pts)

        # max width, max height
        output = cv2.warpPerspective(image, M, (width, height))

        return output
    except:
        get_stacktrace()
        return image


def four_point_transform(pts=None):
    # POC
    final_top_left = (60, 155)
    final_top_right = (155, 60)
    final_bottom_left = (325, 420)
    final_bottom_right = (420, 325)

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
    hwratio = constants.PAPER_DIMENSIION_HEIGHT / constants.PAPER_DIMENSION_WIDTH  # letter size paper
    scale = int(max_width / constants.PERSPECTIVE_TRANSFORM_SCALE_FACTOR)

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
        get_stacktrace()
        return image


def generate_perspective_transformation_params():
    pass


def resize_image(img, height):
    """
    Resizes an image to the specified height
    :param img:
    :param height:
    :return:
    """
    ratio = float(height) / img.shape[0]
    dim = (int(img.shape[1]*ratio), height)

    image = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return image


def split_frame(image, number_of_subimages):
    """
    Split an image into a list of subimages
    :param image:
    :param number_of_subimages:
    :return:
    """
    initial_x = image.shape[1]
    initial_y = image.shape[0]

    final_y = int(initial_y / number_of_subimages)

    subimage_list = []

    start_index = 0
    end_index = final_y

    for i in range(number_of_subimages):
        try:
            subimage_list.append(image[:][start_index:end_index])
            start_index = end_index + 1
            end_index += final_y
        except Exception as e:
            get_stacktrace()

    return subimage_list


def get_roi(img, points):
    """
    Returns image after being cropped to coordinates defined by the list points
    :param img:
    :param points:
    :return:
    """
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


def get_colour_bgr(img, point):
    """
    Returns the colour in BGR format for an image at a specified point (x,y)
    """
    colour = img[point[0]][point[1]].ravel().tolist()
    return colour


def get_colour_hsv(img, point):
    """
    Returns the colour in BGR format for an image at a specified point (x,y)
    """
    try:
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    except Exception as e:
        get_stacktrace()
        img_hsv = img
    colour = img[point[0]][point[1]].ravel().tolist()
    colour[0] = int(colour[0] * 2)
    colour[1] = int(colour[1] / 255.0 * 100.0)
    colour[2] = int(colour[2] / 255.0 * 100.0)
    return colour


def get_stacktrace():
    import traceback
    print("======================")
    print("<< Exception caught >>")
    print("======================")
    traceback.print_exc()
    print("======================")
    error = traceback.format_exc()
    write_to_log(error)
    return error


class PIDController:
    def __init__(self, start_value=0):
        self.error_integral = 0
        self.k_p = 1
        self.k_i = 1
        self.k_d = 0
        self.value = start_value

    def compute_error(self, desired_value):
        return desired_value - self.value

    def compute_next_value(self, desired_value):
        pass

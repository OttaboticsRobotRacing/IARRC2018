import cv2
import numpy as np
import math
from . import utility
import logging

NUMBER_OF_SUBDIVISIONS = 5
CLUSTER_MIN_SIZE = 10

def compute_turn_angle(image):
    # segment the frame horizontally
    subframe_list = split_frame(image, NUMBER_OF_SUBDIVISIONS)

    # get line segments
    # 2D array - list of lists of line segments
    list_of_segment_lists = []
    for subframe in subframe_list:
        line_segments, _ = get_line_segments(subframe)
        list_of_segment_lists.append(line_segments)

    # cluster lines by angle
    clusters_list = []
    for segment_list in list_of_segment_lists:
        if len(segment_list) != 0:
            clusters_list.append(cluster_by_angle(segment_list))  # cluster by angle takes a list of Line objects

    # find longest line cluster
    raw_output_list = []
    for clusters in clusters_list:
        # TODO: need to somehow find the longest cluster in a list of clusters
        # each cluster is a list of line segments
        # cluster_list is a 3D array

        largest_cluster_length = 0
        largest_cluster = None
        for cluster in clusters:
            cluster_magnitude = compute_cluster_magnitude(cluster)
            if cluster_magnitude > largest_cluster_length:
                largest_cluster_length = cluster_magnitude
                largest_cluster = cluster

        raw_output_list.append(compute_cluster_direction(largest_cluster))

    # logging message
    logging.debug('pathfinder.compute_turn_angle()')
    logging.debug('raw_output_list: %s' % raw_output_list)

    # generate weights for each subframe
    #num_nonzero_segment_lists = sum(len(x) > 0 for x in list_of_segment_lists)
    weight_list = generate_weight_list(NUMBER_OF_SUBDIVISIONS)
    #weight_list = generate_weight_list(num_nonzero_segment_lists)


    # apply weighted sum to dominant line angles
    weighted_output_angle_list = []
    for i, output_angle in enumerate(raw_output_list):
        weighted_output = weight_list[i] * output_angle
        weighted_output_angle_list.append(weighted_output)

    # set final output angle to the sum of angles (with weights applied)
    final_output_angle = 0
    for output_angle in weighted_output_angle_list:
        final_output_angle += output_angle

    return final_output_angle


# Helper classes and functions

class Line:
    def __init__(self, x1, y1, x2, y2):
        # set start and end points
        self.p1 = (x1, y1)
        self.p2 = (x2, y2)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        # set length
        self.length = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

        # compute line angle
        dx = x2 - x1
        dy = y2 - y1
        rads = math.atan2(-dy, dx)
        rads %= 2 * math.pi
        degs = -math.degrees(rads)
        if degs <= -180:
            degs += 180
        degs += 90
        self.angle = degs

        # set midpoint
        self.midpoint = (((x1 + x2) / 2), ((y1 + y2) / 2))

    def __str__(self):
        return str(self.angle)

    def __repr__(self):
        return self.__str__()

    def get_coords(self):
        return self.p1, self.p2


class Cluster:
    def __init__(self, cluster):
        self.cluster = cluster
        self.magnitude = compute_cluster_magnitude(cluster)
        self.position = compute_cluster_position(cluster)


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
    '''
    max_line_gap = 5
    min_line_length = 50
    threshold = 20
    '''
    max_line_gap = 20
    min_line_length = 5
    threshold = 1


    lines = cv2.HoughLinesP(mask_edges, 1, np.pi/180, threshold, min_line_length, max_line_gap)

    # create list of Line objects
    line_object_list = []

    try:
        for line in lines:
            # print repr(line)
            x1 = line[0][0]
            y1 = line[0][1]
            x2 = line[0][2]
            y2 = line[0][3]
            line_object_list.append(Line(x1, y1, x2, y2))
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    except:
        pass

    return line_object_list, image


def cluster_by_angle(line_list):
    clusters = []
    last_angle = -180

    for line in line_list:
        if abs(last_angle - line.angle) > 5:
            clusters.append([line])
        else:
            clusters[-1].append(line)
        last_angle = line.angle
    return clusters


def cluster_by_proximity(image, line_list):
    clusters = []

    for line in line_list:
        clusters.append([line])
        for query_line in line_list:
            distance = compute_point_distance(line.midpoint, query_line.midpoint)
            if distance <= 100 and abs(line.angle - query_line.angle) < 10:
                clusters[-1].append(query_line)
                cv2.line(image, line.midpoint, query_line.midpoint, (128, 128, 128), 1)

    filtered_clusters = []
    for cluster in clusters:
        if len(cluster) >= CLUSTER_MIN_SIZE:
            filtered_clusters.append(cluster)

    return image, filtered_clusters


def compute_point_distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    return abs(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))


def compute_cluster_position(cluster):
    """

    :param cluster:
    :return:
    """
    x_total = 0
    y_total = 0

    for line in cluster:
        x_total += line.midpoint[0]
        y_total += line.midpoint[1]

    return x_total / len(cluster), y_total / len(cluster)


def compute_cluster_magnitude(cluster):
    """

    :param cluster:
    :return:
    """
    length = 0

    for line in cluster:
        length += line.length

    return length


def compute_cluster_direction(cluster):
    angle_sum = 0
    for line_segment in cluster:
        angle_sum += line_segment.angle

    return angle_sum / len(cluster)


def generate_weight_list(number_of_weights):
    weight_list = []
    for i in range(number_of_weights):
        weight_list.append(1.0 / 2**(i+1))

    weight_sum = 0
    for w in weight_list:
        weight_sum += w

    weight_diff = 1 - weight_sum
    weight_comp = weight_diff / number_of_weights

    for i, w in enumerate(weight_list):
        weight_list[i] += weight_comp

    weight_sum = 0
    for w in weight_list:
        weight_sum += w

    # logging message
    logging.debug('pathfinder.generate_weight_list()')
    logging.debug('weight_list: %s' % weight_list)
    logging.debug('weight_sum: %s' % weight_sum)

    return weight_list


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
            utility.get_stacktrace()

    return subimage_list

def main():
    logging.basicConfig(level=logging.DEBUG)

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            frame = utility.resize_image(frame, 480)
            print('Output turn angle: %s' % compute_turn_angle(frame))
            cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

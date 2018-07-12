import cv2
import numpy as np
from clusterpathfinder import pathfinding as pathfinder
from calibration import CameraCalibration
import binarization_utils
import matplotlib.pyplot as plt
import line_utils
from line_utils import Line
from globals import xm_per_pix, time_window

global line_lt, line_rt, processed_frames

line_lt = Line(buffer_len=time_window)  # line on the left of the lane
line_rt = Line(buffer_len=time_window) # line on the right of the lane
processed_frames = 0

def debug_roi( img , src_pts , dst_pts , debug=False ):
    '''debug_region of interest

    Extract the interest on top of the image and return it

    Args:
        img:(np.ndarray) image to be draw on
        src_pts: source point to be transform
        dst_pts: destination point to be transform

    Return:
        result:( tuple of np.ndarray ) source image and transform image

    '''
    src_pts  , dst_pts = region_of_interest( img )
    pts = [ tuple(pt) for pt in src_pts[0] ]
    pt0 , pt1 , pt2 , pt3 = pts
    '''
    cv2.line( img , pt0 , pt1 , (0, 0 , 255 ), 1)
    cv2.line( img , pt1 , pt2 , (0, 0 , 255 ), 1)
    cv2.line( img , pt2 , pt3 , (255, 0 , 0 ), 1)
    cv2.line( img , pt3 , pt0 , (255, 0 , 0 ), 1)
    '''
    img_warped, M, Minv = get_birds_eye_view(img , src_pts , dst_pts )
    return img , img_warped



def region_of_interest( img ):
    '''region_of_interest

    Extract the region of interest of the image

    Arguments:
        img:(np.darray) image

    Return:
        collective points of the image region of interest
    '''

    imshape= img.shape
    # Format as ( 0 y , 1 x , channels )
    #=======================================
    # For GTA5
    #=======================================
    # vertices = np.array([
    #     [(.63*imshape[1], 0.30*imshape[0]),
    #      (imshape[1]    ,imshape[0]),
    #      (0,imshape[0]),
    #      (.45*imshape[1], 0.30*imshape[0])]],
    #     dtype=np.float32)

    '''
    vertices = np.array([
        [(.57*imshape[1], 0.42*imshape[0]),
         (imshape[1]    ,.81*imshape[0]),
         (0,.7*imshape[0]),
         (.40*imshape[1], 0.42*imshape[0])]],
        dtype=np.float32)
    '''

    height_factor = 0.3
    width_factor = 0.2
    lower_width_factor = 0.3

    vertices = np.array([
        [((0.5+width_factor)*imshape[1],    height_factor*imshape[0]), # top right
         (imshape[1]+imshape[1]*lower_width_factor,                       imshape[0]), # bottom right
         (0-imshape[1]*lower_width_factor,                                imshape[0]), # bottom left
         ((0.5-width_factor)*imshape[1],    height_factor*imshape[0])]], # top left
        dtype=np.float32)



    src = np.float32(vertices)

    '''
    dst = np.float32([
                      [0.75*img.shape[1],0],
                      [0.75*img.shape[1],img.shape[0]+150],
                      [0.25*img.shape[1],img.shape[0]+150],
                      [0.25*img.shape[1],0]])
    '''
    dst = np.float32([
                      [img.shape[1],    0],
                      [img.shape[1],    img.shape[0]],
                      [0,               img.shape[0]],
                      [0,               0]])




    return src , dst

def get_birds_eye_view( img , src_pts , dst_pts ):
    '''get_birds_eye_view

    Fit Transform geomtric region of the data to
    a Wrapped perspective for a bird view prediction

    Arguments:
        img:(np.darray) image to be transform to
        src_pts:(np.darray) source points for image region
        dst_pts: (np.darray) destination points of image region

    Returns:
        Warpped Perspective

    '''

    img_size = (img.shape[ 1 ] , img.shape[0])

    M    = cv2.getPerspectiveTransform(np.float32(src_pts), np.float32(dst_pts))
    Minv = cv2.getPerspectiveTransform(np.float32(dst_pts), np.float32(src_pts))

    return cv2.warpPerspective(img, M , img_size ), M, Minv


def filter_hsv_colour(img, upper_thresh, lower_thresh):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_thresh, upper_thresh)
    res = cv2.bitwise_and(img, img, mask=mask)

    return mask, res


def compute_offset_from_center(line_lt, line_rt, frame_width):
    """
    Compute offset from center of the inferred lane.
    The offset from the lane center can be computed under the hypothesis that the camera is fixed
    and mounted in the midpoint of the car roof. In this case, we can approximate the car's deviation
    from the lane center as the distance between the center of the image and the midpoint at the bottom
    of the image of the two lane-lines detected.
    :param line_lt: detected left lane-line
    :param line_rt: detected right lane-line
    :param frame_width: width of the undistorted frame
    :return: inferred offset
    """
    if line_lt.detected and line_rt.detected:
        line_lt_bottom = np.mean(line_lt.all_x[line_lt.all_y > 0.95 * line_lt.all_y.max()])
        line_rt_bottom = np.mean(line_rt.all_x[line_rt.all_y > 0.95 * line_rt.all_y.max()])
        lane_width = line_rt_bottom - line_lt_bottom
        midpoint = frame_width / 2
        offset_pix = abs((line_lt_bottom + lane_width / 2) - midpoint)
        offset_meter = xm_per_pix * offset_pix
    else:
        offset_meter = -1

    return offset_meter


def prepare_out_blend_frame(blend_on_road, img_binary, img_birdeye, img_fit, line_lt, line_rt, offset_meter):
    """
    Prepare the final pretty pretty output blend, given all intermediate pipeline images
    :param blend_on_road: color image of lane blend onto the road
    :param img_binary: thresholded binary image
    :param img_birdeye: bird's eye view of the thresholded binary image
    :param img_fit: bird's eye view with detected lane-lines highlighted
    :param line_lt: detected left lane-line
    :param line_rt: detected right lane-line
    :param offset_meter: offset from the center of the lane
    :return: pretty blend with all images and stuff stitched
    """
    h, w = blend_on_road.shape[:2]

    thumb_ratio = 0.2
    thumb_h, thumb_w = int(thumb_ratio * h), int(thumb_ratio * w)

    off_x, off_y = 20, 15

    # add a gray rectangle to highlight the upper area
    mask = blend_on_road.copy()
    mask = cv2.rectangle(mask, pt1=(0, 0), pt2=(w, thumb_h+2*off_y), color=(0, 0, 0), thickness=cv2.FILLED)
    blend_on_road = cv2.addWeighted(src1=mask, alpha=0.2, src2=blend_on_road, beta=0.8, gamma=0)

    # add thumbnail of binary image
    thumb_binary = cv2.resize(img_binary, dsize=(thumb_w, thumb_h))
    thumb_binary = np.dstack([thumb_binary, thumb_binary, thumb_binary]) * 255
    blend_on_road[off_y:thumb_h+off_y, off_x:off_x+thumb_w, :] = thumb_binary

    # add thumbnail of bird's eye view
    thumb_birdeye = cv2.resize(img_birdeye, dsize=(thumb_w, thumb_h))
    thumb_birdeye = np.dstack([thumb_birdeye, thumb_birdeye, thumb_birdeye]) * 255
    blend_on_road[off_y:thumb_h+off_y, 2*off_x+thumb_w:2*(off_x+thumb_w), :] = thumb_birdeye

    # add thumbnail of bird's eye view (lane-line highlighted)
    thumb_img_fit = cv2.resize(img_fit, dsize=(thumb_w, thumb_h))
    blend_on_road[off_y:thumb_h+off_y, 3*off_x+2*thumb_w:3*(off_x+thumb_w), :] = thumb_img_fit

    # add text (curvature and offset info) on the upper right of the blend
    mean_curvature_meter = np.mean([line_lt.curvature_meter, line_rt.curvature_meter])
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(blend_on_road, 'Curvature radius: {:.02f}m'.format(mean_curvature_meter), (860, 60), font, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(blend_on_road, 'Offset from center: {:.02f}m'.format(offset_meter), (860, 130), font, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

    return blend_on_road




def main():
    cap = cv2.VideoCapture('footage/3_edit.avi')
    '''
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    '''

    DIM = (640, 480)
    K = np.array([[359.0717640266508, 0.0, 315.08914578097387], [0.0, 358.06497428501837, 240.75242680088732], [0.0, 0.0, 1.0]])
    D = np.array([[-0.041705903204711826], [0.3677107787593379], [-1.4047363783373128], [1.578157237454529]])
    profile = (DIM, K, D)
    CC = CameraCalibration(profile)

    yellow_HSV_th_min = np.array([0, 70, 70])
    yellow_HSV_th_max = np.array([50, 255, 255])

    line_lt = Line(buffer_len=time_window)  # line on the left of the lane
    line_rt = Line(buffer_len=time_window) # line on the right of the lane
    processed_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()

        frame = CC.undistort(frame)

        ### calibration ###


        ### crop to ROI ###
        ### perspective transform ###


        img, warped = debug_roi(frame, None, None)


        ### binarize frame ###




        ### get steering angle v1 ###

        '''
        _, lines = pathfinder.get_line_segments(warped)
        grey = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        turn_angle = pathfinder.compute_turn_angle(grey)
        print('turn angle:', turn_angle)

        cv2.imshow('lines', lines)
        '''

        ### get steering angle v2 ###

        #mask, res = filter_hsv_colour(img, yellow_HSV_th_max, yellow_HSV_th_min)

        img_binary = binarization_utils.binarize(warped, verbose=False)
        cv2.imshow('img binary', img_binary)


        img_binary_colour = cv2.cvtColor(img_binary, cv2.COLOR_GRAY2BGR)
        #img_binary_colour = img_binary_colour[:][100:]
        _, lines = pathfinder.get_line_segments(img_binary_colour)
        cv2.imshow('lines', lines)
        turn_angle = pathfinder.compute_turn_angle(img_binary)
        print('turn angle:', turn_angle)


        '''
        keep_state = False


        if processed_frames > 0 and keep_state and line_lt.detected and line_rt.detected:
            line_lt, line_rt, img_fit = line_utils.get_fits_by_previous_fits(img_binary, line_lt, line_rt, verbose=False)
        else:
            line_lt, line_rt, img_fit = line_utils.get_fits_by_sliding_windows(img_binary, line_lt, line_rt, n_windows=9, verbose=False)

        offset_meter = compute_offset_from_center(line_lt, line_rt, frame_width=frame.shape[1])
        '''
        #print(offset_meter)

        #Minv = np.zeros(shape=(3, 3))

        # draw the surface enclosed by lane lines back onto the original frame
        #blend_on_road = line_utils.draw_back_onto_the_road(img, Minv, line_lt, line_rt, keep_state)

        #cv2.imshow('asfdfd', blend_on_road)

        # stitch on the top of final output images from different steps of the pipeline
        #blend_output = prepare_out_blend_frame(blend_on_road, img_binary, warped, img_fit, line_lt, line_rt, offset_meter)

        #processed_frames += 1

        #cv2.imshow('mask', mask)
        #cv2.imshow('res', res)



        cv2.imshow('frame', frame)
        cv2.imshow('warped', warped)


        if cv2.waitKey(100) & 0xFF == ord('q'):
                break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

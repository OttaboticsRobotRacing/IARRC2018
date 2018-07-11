import cv2
import numpy as np
from clusterpathfinder import pathfinding as pathfinder
from calibration import CameraCalibration

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

    height_factor = 0.4
    width_factor = 0.1

    vertices = np.array([
        [((0.5+width_factor)*imshape[1],    height_factor*imshape[0]), # top right
         (imshape[1],                       imshape[0]), # bottom right
         (0,                                imshape[0]), # bottom left
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

    while cap.isOpened():
        ret, frame = cap.read()

        frame = CC.undistort(frame)

        ### calibration ###


        ### crop to ROI ###
        ### perspective transform ###


        img, warped = debug_roi(frame, None, None)

        _, lines = pathfinder.get_line_segments(warped)

        ### get steering angle ###

        grey = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        turn_angle = pathfinder.compute_turn_angle(grey)
        print('turn angle:', turn_angle)








        cv2.imshow('frame', frame)
        #cv2.imshow('warped', warped)
        cv2.imshow('lines', lines)


        if cv2.waitKey(200) & 0xFF == ord('q'):
                break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

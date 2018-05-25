import abc
import cv2

class PathfinderInterface(abc.ABC):
    @abc.abstractmethod
    def calculate_angle(self, image):
        """
        Pathfinder interface method to be implemented by pathfinding strategies.
        Calculates steering angle from an OpenCV image

        Args:
            image (numpy.ndarray): OpenCV input image

        Returns:
            int: steering angle between -90 and 90
        """
        pass

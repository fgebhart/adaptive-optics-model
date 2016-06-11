__author__ = 'Fabian Gebhart'

# This file "just_cam.py" simply displays the image captured by
# the camera to the user. It will also display the reference
# lines and the number of the found laser points. For more info
# see: https://github.com/fgebhart/adaptive-optics-model


# import the necessary packages
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import RPi.GPIO as GPIO
import os

# enable Pi-Camera and set resolution
camera = PiCamera()
camera.resolution = (256, 256)
rawCapture = PiRGBArray(camera, size=(256, 256))

def get_laser_points(image):
    """Return centers of laser-points found in the given image
    as list of coordinate-tuples."""
    # The color boarders for red laser (appears white on screen)
    whiteLower = (190, 190, 190)
    whiteUpper = (255, 255, 255)
    # get the contour areas for the steppers
    mask = cv2.inRange(image, whiteLower, whiteUpper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    # compute the center of the contour areas
    centroids = []
    for contour in contours:
        m = cv2.moments(contour)
        # avoid division by zero error!
        if m['m00'] != 0:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            centroids.append((cx, cy))
            # following line manages sorting the found contours
            # from left to right, sorting
            # first tuple value (x coordinate) ascending
            centroids = sorted(centroids)

    return centroids


def draw_laser_numbers(image, laser_points):
    """Draw laser numbers on the image next to the given laser
    points"""
    for (i, c) in enumerate(laser_points):
        cx, cy = c
        cv2.putText(image, "{}".format(i + 1),
                    (cx - 5, cy + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (255, 255, 255), 1)


def draw_reference_points_new2(image):
    """Draw evenly distributed reference points on the given
    image"""
    image_height = image.shape[1]
    reference_point_color = (0, 255, 0)
    upper_y = image_height / 2
    lower_y = image_height / 2 - 10
    cv2.line(image, (70, upper_y), (70, lower_y),
     reference_point_color, thickness=1, lineType=8, shift=0)
    cv2.line(image, (99, upper_y), (99, lower_y),
     reference_point_color, thickness=1, lineType=8, shift=0)
    cv2.line(image, (128, upper_y), (128, lower_y),
     reference_point_color, thickness=1, lineType=8, shift=0)
    cv2.line(image, (157, upper_y), (157, lower_y),
     reference_point_color, thickness=1, lineType=8, shift=0)
    cv2.line(image, (186, upper_y), (186, lower_y),
     reference_point_color, thickness=1, lineType=8, shift=0)


def draw_fps(image, start, end):
    """Draw frame-rate information on given image"""
    fps = round((1 / (end - start)), 2)
    cv2.putText(image, "fps:{}".format(fps),
                (image.shape[1]/2 - 25, 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)


def log(*args):
    """function to activate the 'print' commands. Just comment
     or uncomment the following lines"""
    # pass
    print args


# initialize the variables:
lasers_matched = False
laser_positions_initialized = False
laser_positions_reached = False
last_laser_points = None
matched_list = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
goal_position = [70, 99, 128, 157, 186]
pixel_to_steps_coefficient = 0.55
# good results with 0.9
gain_factor = 0.8
# make sure the close.log file is existing in order to
# successfully run this file  - see tk_ao.py
os.system('sudo touch /home/pi/close.log')


# While loop for loading, interpreting and showing frames
while True:
    camera.capture(rawCapture, format="bgr",
                   use_video_port=True)

    start = time.time()
    # grab the rawCapture array representing the image
    image = rawCapture.array

    # find contours in the accumulated image
    laser_points = get_laser_points(image)

    # draw reference lines (green) and (unsorted) laser index
    draw_reference_points_new2(image)
    draw_laser_numbers(image, laser_points)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    end = time.time()
    draw_fps(image, start, end)
    # show the frame
    cv2.imshow("Kamera Bild", image)
    # move frame to given position
    cv2.moveWindow("Kamera Bild", 500, 100)

    # check if the close.log file exists. If it is deleted break
    if os.path.isfile('/home/pi/close.log') is True:
        pass
    else:
        break

    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


GPIO.cleanup()
__author__ = 'Fabian Gebhart'

# This file "AO_just_stabi.py" provides the main programm for
# the Adaptive Optics Model. It establishes the interface
# between camera input and stepper output. Each given error is
# transformed in a corresponding correction. This script
# realizes the live correction in closed-loop setup. For more
# info see: https://github.com/fgebhart/adaptive-optics-model


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

# Time delay for stepper motors 0.0008 is smallest working delay
# looks like 0.001 works better... stepper moving more smooth
delay = 0.001

# Movement pattern for "half-stepping" method, counter clockwise
#    [1, 0, 0, 0],   # 0
#    [1, 1, 0, 0],   # 1
#    [0, 1, 0, 0],   # 2
#    [0, 1, 1, 0],   # 3
#    [0, 0, 1, 0],   # 4
#    [0, 0, 1, 1],   # 5
#    [0, 0, 0, 1],   # 6
#    [1, 0, 0, 1]]   # 7

# same movement pattern, but only editing the different bits,
# leads to better performance (= smaller delay)
MOVE_PATTERN = [
    (1, GPIO.HIGH),  # to 1
    (0, GPIO.LOW),   # to 2
    (2, GPIO.HIGH),  # ...
    (1, GPIO.LOW),
    (3, GPIO.HIGH),
    (2, GPIO.LOW),
    (0, GPIO.HIGH),
    (3, GPIO.LOW)    # to 0
    ]

# Set "GPIO-Mode" to BCM = Board Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

number_of_steppers = 5

stepperPins = [
# ___0___1___2___3
    [6, 13, 19, 26],    # stepper 1
    [12, 16, 20, 21],   # stepper 2
    [14, 15, 18, 23],   # stepper 3
    [7, 8, 25, 24],     # stepper 4
    [22, 27, 17, 4]]    # stepper 5

# define the pins of the steppers as outputs
GPIO.setup(stepperPins[0], GPIO.OUT)
GPIO.setup(stepperPins[1], GPIO.OUT)
GPIO.setup(stepperPins[2], GPIO.OUT)
GPIO.setup(stepperPins[3], GPIO.OUT)
GPIO.setup(stepperPins[4], GPIO.OUT)

# initialize steppers to INIT_PATTERN, that is, the first part
# of the sequence
for stepper in stepperPins:
    GPIO.output(stepper[0], 1)
    GPIO.output(stepper[1], 0)
    GPIO.output(stepper[2], 0)
    GPIO.output(stepper[3], 0)

# Current position of the steppers in the move-sequence: relates
# to MOVE_PATTERN
stepperPositions = [0, 0, 0, 0, 0]

def get_laser_points(image):
    """Return centers of laser-points found in the given image
    as list of coordinate-tuples."""
    # The color boundaries for red laser (appears white on screen)
    # are in GBR: green, blue, red
    whiteLower = (150, 150, 180)
    whiteUpper = (255, 255, 255)
    # these boundaries should work fine for even bright rooms
    # rooms with dimmed light should apply new lower
    # boundaries: (190, 190, 190)
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
            # from left to right(sorting first tuple value
            # x coordinate) ascending
            centroids = sorted(centroids)
            centroids = centroids[:5]


    return centroids


def move_steppers(steps_to_perform_per_stepper):
    """Moves all steppers in parallel for the given movement
    parameters. steps_to_perform_per_stepper is a list like:
    [2, 400, 0, -20, -200]"""
    absolute_list = [0, 0, 0, 0, 0]

    for i in range(number_of_steppers):
        absolute_list[i] = abs(steps_to_perform_per_stepper[i])
    max_steps = max(absolute_list)
    for step in range(max_steps):
        for stepper in range(number_of_steppers):
            if abs(steps_to_perform_per_stepper[stepper])\
                    > step:
                if steps_to_perform_per_stepper[stepper] < 0:
                # CLOCK-WISE
                    stepperPositions[stepper] -= 1
                    move =\
                        MOVE_PATTERN[stepperPositions[stepper]
                                     % len(MOVE_PATTERN)]
                    move = (move[0], not move[1])
                else:  # COUNTER-CLOCK-WISE
                    move =\
                        MOVE_PATTERN[stepperPositions[stepper]
                                        % len(MOVE_PATTERN)]
                    stepperPositions[stepper] += 1
                pins = stepperPins[stepper]
                GPIO.output(pins[move[0]], move[1])
        time.sleep(delay)


def log(*args):
    """function to activate the 'print' commands. Just comment
     or uncomment the following lines"""
    #pass
    print args


def find_movement_on_screen(last_laser_points,
                            current_laser_points):
    """Manages to find movement on screen. If coordinates move
    more then 3 px the list with the found coordinates is
    returned"""
    threshold = 3
    # creates a list with the x coordinates of the laserspots of
    # the current and the last frame
    difference_list = [a[0] - b[0] for a, b in
                zip(last_laser_points, current_laser_points)]
    #log("difference_list: ", difference_list)
    for i in range(0, len(difference_list)):
        if abs(difference_list[i]) > threshold:
            return current_laser_points[i]


def stabilize_laser(laser_points):
    """function to stabilize the laser on their goal position.
    Trying to keep them there."""
    way_to_correct = [0, 0, 0, 0, 0]
    for i in range(0, len(laser_points)):
        way_to_correct[i] =\
            int(((laser_points[i][0] - goal_position[i])
                            * pixel_to_steps_coefficient)
                            * gain_factor)
    #log("way to correct: ", way_to_correct)
    move_steppers(way_to_correct)


# initialize the variables:
lasers_matched = False
laser_positions_initialized = False
last_laser_points = None
matched_list = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
# original position: goal_position = [70, 99, 128, 157, 186]
goal_position = [70, 99, 128, 157, 186]
pixel_to_steps_coefficient = 0.55
# good results with 0.9
gain_factor = 0.8
# make sure the close.log file is existing in order to
# successfully run this file - see tk_ao.py
os.system('sudo touch /home/pi/close.log')


# While loop for loading, interpreting and showing frames
while True:
    camera.capture(rawCapture, format="bgr",
                   use_video_port=True)

    # grab the rawCapture array representing the image
    image = rawCapture.array

    # find contours in the accumulated image
    laser_points = get_laser_points(image)
    # limit number of found centers to number of steppers
    laser_points = laser_points[:number_of_steppers]

    # figure out if all five lasers are on screen:
    if len(laser_points) == 5:
        laser_positions_reached = True
    else:
        laser_positions_reached = False

    # if all lasers reached their goal position, stabilize them
    if laser_positions_reached is True:
        stabilize_laser(laser_points)

    # set current laser points to last laser points to allow
    # movement tracking for "find_movement_on_screen"
    last_laser_points = laser_points

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

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

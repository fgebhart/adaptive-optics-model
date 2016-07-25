__author__ = 'Fabian Gebhart'

# This file "AO_reset.py" resets the Adaptive Optics Model, to
# start all over again. If, for any reason, the main program
# should be confused or # messed up. Just quit it and run this
# file. It iterates through all # steppers and assigns the
# found (moving) laser points. For more info see:
# https://github.com/fgebhart/adaptive-optics-model


# import the necessary packages
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import RPi.GPIO as GPIO
import os

# make sure the close.log file is existing in order to
# successfully run this file  - see tk_ao.py
os.system('sudo touch /home/pi/close.log')

# allow camera to wake up
# time.sleep(2)

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
    # boundaries are in GBR: green, blue, red
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
            # from left to right, sorting
            # first tuple value (x coordinate) ascending
            centroids = sorted(centroids)
            centroids = centroids[:5]


    return centroids


def move_stepper(stepper, steps_to_perform):
    """Moves only one stepper. stepper = 0,1,2,3,4;
    steps_to_perform = -4096...+4096"""
    pins = stepperPins[stepper]
    for step in range(abs(steps_to_perform)):
        if steps_to_perform < 0:  # CLOCK-WISE
            stepperPositions[stepper] -= 1
            move = MOVE_PATTERN[stepperPositions[stepper]
                                % len(MOVE_PATTERN)]
            move = (move[0], not move[1])
        else:  # > 0  COUNTER-CLOCK-WISE
            move = MOVE_PATTERN[stepperPositions[stepper]
                                % len(MOVE_PATTERN)]
            stepperPositions[stepper] += 1
        GPIO.output(pins[move[0]], move[1])
        time.sleep(delay)


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
    pass
    # print args


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
    log("difference_list:", difference_list)
    for i in range(0, len(difference_list)):
        if abs(difference_list[i]) > threshold:
            return current_laser_points[i]


def match_laser_to_stepper(matched_list):
    """moves the current stepper in order to find a movement on
    the screen. If movement is found, the current stepper is
    assigned to found coordinates of the laser"""
    step_size = 2
    current_stepper = 0

    # find out which laser is not yet matched to determine the
    # stepper to move
    for i in range(0, number_of_steppers):
        if matched_list[i] == (0, 0):
            current_stepper = i
            break

    # check if last_laser_points is already fetched (here it
    # needs to buffer at least one frame to avoid finding
    # "movement in the first frame")
    if last_laser_points is not None:
        if len(last_laser_points) > len(laser_points):
            # if laser left screen, we got to move it even more
            # (8) backwards to enter screen again
            move_stepper(current_stepper, (-1) * step_size * 20)
        else:
            # check out the value of the matched_list and find
            # the relating lasers where value == 0
            if matched_list[current_stepper] == (0, 0):
                # if there is no movement on the screen
                # -> keep turning the current stepper
                if find_movement_on_screen(last_laser_points,
                                       laser_points) is None:
                        move_stepper(current_stepper,
                                    step_size * 16)
                # else: Movement is found, store it in the
                # matched_list at index "current_stepper"
                else:
                    matched_list[current_stepper]\
                    = find_movement_on_screen(last_laser_points,
                                                  laser_points)
                    log("inserted coordinates in matched_list,"
                        "switching to next stepper")
                    log("matched list:", matched_list)
                    current_stepper += 1
                    return None
            else:
                log("All lasers are matched to the steppers")
                log("matched list:", matched_list)
                return matched_list


def get_laser_on_position(matched_list):
    """Move lasers to their starting (goal) position"""
    # initialize lists
    way_to_go_in_steps = [0, 0, 0, 0, 0]

    log("goal position:", goal_position)

    # calculating the way from current position (matched_list)
    # to start_position
    for i in range(0, len(matched_list)):
        way_to_go_in_steps[i] = int((matched_list[i][0]
             - goal_position[i])* pixel_to_steps_coefficient)
        # determine direction, whether laser is left or right of
        # the starting position
    log("way to go in steps:", way_to_go_in_steps)
    log("Attention... Moving Steppers")
    time.sleep(2)
    move_steppers(way_to_go_in_steps)


def stabilize_laser(laser_points):
    """function to stabilize the laser on their goal position.
    Trying to keep them there."""
    way_to_correct = [0, 0, 0, 0, 0]
    for i in range(0, len(laser_points)):
        way_to_correct[i] = int(((laser_points[i][0]
              - goal_position[i]) * pixel_to_steps_coefficient)
                                * gain_factor)
    log("way to correct:", way_to_correct)
    move_steppers(way_to_correct)


# initialize the variables:
lasers_matched = False
laser_positions_initialized = False
laser_positions_reached = False
last_laser_points = None
matched_list = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
goal_position = [70, 99, 128, 157, 186]
# pixel_to_steps_coefficient = 0.55
pixel_to_steps_coefficient = 0.55
# good results with 0.9
gain_factor = 0.3
# counter for letting it run 5 more images to stabilize
# the lasers
counter = 0
# another counter for letting the camera warmup
# in order to avoid missing the first movement
warm_up_cocunter = 0


# While loop for loading, interpreting and showing frames
while True:
    camera.capture(rawCapture, format="bgr",
                   use_video_port=True)

    # grab the raw NumPy array representing the image, then
    # initialize the timestamp
    # and occupied/unoccupied text
    image = rawCapture.array

    # find contours in the accumulated image
    laser_points = get_laser_points(image)
    # limit number of found centers to number of steppers
    laser_points = laser_points[:number_of_steppers]

    # if all lasers reached their goal position, stabilize them
    # (move this code to the beginning, so it works with the
    # new laser points and stabilizes them)
    if laser_positions_reached is True:
        stabilize_laser(laser_points)
        # having 5 more frames to stabilize and then
        # end program
        if counter < 5:
            counter += 1
        else:
            break

    # if lasers are not matched, do so...
    if not lasers_matched:
        matched_lasers = match_laser_to_stepper(matched_list)
        # if they are now matched, match_laser_to_stepper
        # returns the list, no more "none"
        if matched_lasers is not None:
            lasers_matched = True

    # if lasers are matched and laser_position_reached is False
    # then run "get_laser_on_position" once (!)
    if lasers_matched and not laser_positions_reached:
        get_laser_on_position(matched_list)
        laser_positions_reached = True


    # set current laser points to last laser points to allow
    # movement tracking for "find_movement_on_screen"
    last_laser_points = laser_points

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # check if the close.log file exists. If it is deleted break
    if os.path.isfile('/home/pi/close.log') is False:
        break

    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

GPIO.cleanup()
os.remove('/home/pi/close.log')

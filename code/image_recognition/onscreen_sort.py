# import the necessary packages
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import RPi.GPIO as GPIO
from random import randint

camera = PiCamera()
camera.resolution = (256, 256)
rawCapture = PiRGBArray(camera, size=(256, 256))

# allow the camera to warmup
time.sleep(0.5)

whiteLower = (200, 200, 200)  # diese Einstellung funktioniert fuer roten Laser
whiteUpper = (255, 255, 255)

##########################
# SETUP & INITIALIZATION #
##########################
delay = 0.0008 # 0.00055

# Bewegungsmuster, dass fuer Half-Stepping benutzt wird, um eine Sequenz durchzufuehren (gegen den Uhrzeigersinn)
#    [1, 0, 0, 0],   # 0
#    [1, 1, 0, 0],   # 1
#    [0, 1, 0, 0],   # 2
#    [0, 1, 1, 0],   # 3
#    [0, 0, 1, 0],   # 4
#    [0, 0, 1, 1],   # 5
#    [0, 0, 0, 1],   # 6
#    [1, 0, 0, 1]]   # 7

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

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

number_of_steppers = 5

#find random number 0 or 1 for stepper movement
random_stepper_direction = randint(0,1)

stepperPins = [
#    0   1   2   3
    [6, 13, 19, 26],    # stepper 1
    [12, 16, 20, 21],   # stepper 2
    [14, 15, 18, 23],   # stepper 3
    [24, 25, 8, 7],     # stepper 4
    [4, 17, 27, 22]]    # stepper 5

# define the pins of the steppers as outputs
GPIO.setup(stepperPins[0], GPIO.OUT)
GPIO.setup(stepperPins[1], GPIO.OUT)
GPIO.setup(stepperPins[2], GPIO.OUT)
GPIO.setup(stepperPins[3], GPIO.OUT)
GPIO.setup(stepperPins[4], GPIO.OUT)

# initialize steppers to INIT_PATTERN, that is, the first part of the sequence
for stepper in stepperPins:
    GPIO.output(stepper[0], 1)
    GPIO.output(stepper[1], 0)
    GPIO.output(stepper[2], 0)
    GPIO.output(stepper[3], 0)
    #time.sleep(delay * 4)

# Current position of the steppers in the move-sequence: relates to MOVE_PATTERN
stepperPositions = [0, 0, 0, 0, 0]


def get_laser_points(image):
    """
    Return centers of laser-points found in the given image as list of coordinate-tuples.
    """
    # get the contour areas for the steppers
    mask = cv2.inRange(image, whiteLower, whiteUpper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # compute the center of the contour areas
    centroids = []
    for contour in contours:
        m = cv2.moments(contour)
        # avoid division by zero error!
        if m['m00'] != 0:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            centroids.append((cx, cy))

    return centroids


def draw_laser_numbers(image, laser_points):
    """Draw laser numbers on the image next to the given laser points"""
    for (i, c) in enumerate(laser_points):
        cx, cy = c
        cv2.putText(image, "#{}".format(i + 1), (cx - 5, cy + 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (255, 255, 255), 1)


def draw_reference_points(image, number_of_reference_points):
    """Draw evenly distributed reference points on the given image"""
    reference_point_color = (0, 255, 0)
    image_width = image.shape[0]
    image_height = image.shape[1]
    upper_y = image_height / 2 + 30
    lower_y = image_height / 2 + 20
    step_width = image_width / number_of_reference_points
    start_offset = step_width / 2
    for x in range(start_offset, image_width, step_width):
        cv2.line(image, (x, upper_y), (x, lower_y), reference_point_color, thickness=1, lineType=8, shift=0)


def draw_fps(image, start, end):
    """Draw frame-rate information on given image"""
    fps = round((1 / (end - start)), 2)
    cv2.putText(image, "fps:{}".format(fps), (image.shape[1]/2 - 25, 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)


def move_stepper(stepper, direction_to_step, steps_to_perform):
    pins = stepperPins[stepper]
    for step in range(steps_to_perform):
        if direction_to_step == 1:  # CLOCK-WISE
            stepperPositions[stepper] -= 1
            move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
            move = (move[0], not move[1])
        else:  # COUNTER-CLOCK-WISE
            move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
            stepperPositions[stepper] += 1
        GPIO.output(pins[move[0]], move[1])
        time.sleep(delay)

def move_steppers(directions_to_step, steps_to_perform_per_stepper):
    """Moves all steppers in parallel for the given movement parameters."""
    stepper_count = len(directions_to_step)

    maxSteps = max(steps_to_perform_per_stepper)
    for step in range(maxSteps):
        for stepper in range(stepper_count):
            if steps_to_perform_per_stepper[stepper] > step:
                if directions_to_step[stepper] == 1:  # CLOCK-WISE
                    stepperPositions[stepper] -= 1
                    move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
                    move = (move[0], not move[1])
                else:  # COUNTER-CLOCK-WISE
                    move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
                    stepperPositions[stepper] += 1

                pins = stepperPins[stepper]
                GPIO.output(pins[move[0]], move[1])
        time.sleep(delay)


def log(*args):
    pass
    #print args

def find_movement_on_screen(last_laser_points, current_laser_points):
    threshold = 3
    # creates a list with the x coordinates of the laserspots of the current and the last frame
    difference_list = [a[0] - b[0] for a, b in zip(last_laser_points, current_laser_points)]
    print "difference_list:", difference_list
    for i in range(0, len(difference_list)):
        if abs(difference_list[i]) > threshold:
            return current_laser_points[i]


def match_laser_to_stepper(matched_list):
    step_size = 4
    current_stepper = 0

    # find out which laser is not yet matched to determine the stepper to move
    for i in range(0, number_of_steppers):
        if matched_list[i] == (0,0):
            current_stepper = i
            break

    # check if last_laser_points is already fetched (here it needs to buffer at least one frame to avoid finding
    # "movement in the first frame")
    if last_laser_points is not None:
        if len(last_laser_points) > len(laser_points):
            # if laser left screen, we got to move it even more (32) backwards to enter screen again
            # random_stepper_direction -1 *(-1) makes 0 -> 1 and 1 -> 0 which is backwards
            move_stepper(current_stepper, (random_stepper_direction - 1) * (-1), step_size * 32)
        else:
            # check out the value of the matched_list and find the relating lasers where value == 0
            if matched_list[current_stepper] == (0,0):
                # if there is no movement on the screen -> keep turning the current stepper
                if find_movement_on_screen(last_laser_points, laser_points) is None:
                    move_stepper(current_stepper, random_stepper_direction, step_size * 16)
                # else: Movement is found, store it in the matched_list at index "current_stepper"
                else:
                    matched_list[current_stepper] = find_movement_on_screen(last_laser_points, laser_points)
                    print "inserted coordinates in matched_list, switching to next stepper"
                    print "matched list:", matched_list
                    current_stepper += 1
                    return None
            else:
                print "All lasers are matched to the steppers"
                print "matched list:", matched_list
                return matched_list


def get_laser_on_position(matched_list):
    """Move lasers to their starting position"""
    # initialize lists
    direction_to_step = [0,0,0,0,0]
    way_to_go_in_steps = [0,0,0,0,0]

    print "goal position:", goal_position

    # calculating the way from current position (matched_list) to start_position
    for i in range(0, len(matched_list)):
        way_to_go_in_steps[i] = int(abs((goal_position[i] - matched_list[i][0]) * 0.6))
        # determine direction, whether laser is left or right of the starting position
        if matched_list[i][0] > goal_position[i]:
            direction_to_step[i] = 0
        else:
            direction_to_step[i] = 1
    print "directions:", direction_to_step
    print "way to go in steps:", way_to_go_in_steps
    print "Attention... Moving Steppers"
    time.sleep(3)
    move_steppers(direction_to_step, way_to_go_in_steps)

# initialize the variables:
lasers_matched = False
laser_positions_initialized = False
laser_positions_reached = False
last_laser_points = None
matched_list = [(0,0),(0,0),(0,0),(0,0),(0,0)]
goal_position = [26,77,128,179,230]


while True:
    print("====================START=====================")
    camera.capture(rawCapture, format="bgr", use_video_port=True)

    start = time.time()
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = rawCapture.array
    image = cv2.flip(image, -1)

    # find contours in the accumulated image
    #if not laser_positions_initialized:
    laser_points = get_laser_points(image)
    # limit number of found centers to number of steppers
    laser_points = laser_points[:number_of_steppers]
    #laser_positions_initialized = True

    # draw reference lines (green) and (unsorted) laser index
    draw_reference_points(image, number_of_steppers)
    draw_laser_numbers(image, laser_points)


    ######################################MAGIC#############################
    # run main program to match laser and steppers

    print laser_points
    print last_laser_points

    if not lasers_matched:
        matched_lasers = match_laser_to_stepper(matched_list)
        if matched_lasers is not None:
            lasers_matched = True


    #if matched_list[len(matched_list)-1][0] != 0:
    if lasers_matched and not laser_positions_reached:
        get_laser_on_position(matched_list)
        laser_positions_reached = True

    last_laser_points = laser_points

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    end = time.time()
    draw_fps(image, start, end)
    # show the frame
    cv2.imshow("Get Laser on Screen", image)

    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


GPIO.cleanup()
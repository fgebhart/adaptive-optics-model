__author__ = 'Fabian'
import time
import RPi.GPIO as GPIO
from random import randint

# Time delay for stepper motors, 0.00055 is smallest working delay
delay = 0.0009

# Movement pattern for "half-stepping" method, counter clockwise
#    [1, 0, 0, 0],   # 0
#    [1, 1, 0, 0],   # 1
#    [0, 1, 0, 0],   # 2
#    [0, 1, 1, 0],   # 3
#    [0, 0, 1, 0],   # 4
#    [0, 0, 1, 1],   # 5
#    [0, 0, 0, 1],   # 6
#    [1, 0, 0, 1]]   # 7

# same movement pattern, but only editing the different bits, leads to better performance (= smaller delay)
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

# Current position of the steppers in the move-sequence: relates to MOVE_PATTERN
stepperPositions = [0, 0, 0, 0, 0]


def move_stepper(stepper, steps_to_perform):
    """Moves only one stepper. stepper = 0,1,2,3,4; steps_to_perform = -4096...+4096"""
    pins = stepperPins[stepper]
    for step in range(abs(steps_to_perform)):
        if steps_to_perform < 0:  # CLOCK-WISE
            stepperPositions[stepper] -= 1
            move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
            move = (move[0], not move[1])
        else:  # COUNTER-CLOCK-WISE
            move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
            stepperPositions[stepper] += 1
        GPIO.output(pins[move[0]], move[1])
        time.sleep(delay)


def move_steppers(steps_to_perform_per_stepper):
    """Moves all steppers in parallel for the given movement parameters.
    steps_to_perform_per_stepper is a list like: [2, 400, 0, -20, -200]"""
    absolute_list = [0, 0, 0, 0, 0]

    for i in range(number_of_steppers):
        absolute_list[i] = abs(steps_to_perform_per_stepper[i])
    max_steps = max(absolute_list)

    for step in range(max_steps):
        for stepper in range(number_of_steppers):
            if abs(steps_to_perform_per_stepper[stepper]) > step:
                if steps_to_perform_per_stepper[stepper] < 0:  # CLOCK-WISE
                    stepperPositions[stepper] -= 1
                    move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
                    move = (move[0], not move[1])
                else:  # COUNTER-CLOCK-WISE
                    move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
                    stepperPositions[stepper] += 1
                pins = stepperPins[stepper]
                GPIO.output(pins[move[0]], move[1])
        time.sleep(delay)


a = randint(-300, 300)
b = randint(-300, 300)
c = randint(-300, 300)
d = randint(-300, 300)
e = randint(-300, 300)

stepping_list = [a, b, c, d, e]
print stepping_list

move_steppers([a, b, c, d, e])
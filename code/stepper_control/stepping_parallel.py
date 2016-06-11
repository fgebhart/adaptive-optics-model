import time
import RPi.GPIO as GPIO

##########################
# SETUP & INITIALIZATION #
##########################
delay = 0.01

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
    time.sleep(delay * 4)

# Current position of the steppers in the move-sequence: relates to MOVE_PATTERN
stepperPositions = [0, 0, 0, 0, 0]

# From here on, everything is done per frame

###############################
# DETERMINE DELTA PER STEPPER #
###############################

stepsToPerformPerStepper = [4096, 0, 4096, 0, 0]
directionsToStep = [0, 0, 0, 0, 0]       # 1 = CLOCK-WISE, 0 = COUNTER-CLOCK-WISE

################################
# MOVE ALL STEPPERS PARALLELY  #
################################

start = time.time()
maxSteps = max(stepsToPerformPerStepper)
print("maxStep: ", maxSteps)
for step in range(maxSteps):
    #print("====== ", step, "=======")
    for stepper in range(5):
        if stepsToPerformPerStepper[stepper] > step:
            if directionsToStep[stepper] == 1: # CLOCK-WISE
                stepperPositions[stepper] -= 1
                move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
                move = (move[0], not move[1])
            else:  # COUNTER-CLOCK-WISE
                move = MOVE_PATTERN[stepperPositions[stepper] % len(MOVE_PATTERN)]
                stepperPositions[stepper] += 1

            pins = stepperPins[stepper]
            #print(step, stepper, move)
            GPIO.output(pins[move[0]], move[1])
    time.sleep(delay)
print 'It took', time.time()-start, 'seconds.'

GPIO.cleanup()

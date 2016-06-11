import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

delay = 0.001                   # 0.0008 seems to be the smallest possible time
number_of_steppers = 5          # maybe nr4 and nr5 need to warm up a little


# Current position of the steppers in the move-sequence: relates to MOVE_PATTERN
stepperPositions = [0, 0, 0, 0, 0]

#Pin Belegungen der 5 Motoren:
stepperPins = [
# ___0___1___2___3
    [6, 13, 19, 26],    # stepper 1
    [12, 16, 20, 21],   # stepper 2
    [14, 15, 18, 23],   # stepper 3
    [7, 8, 25, 24],     # stepper 4
    [22, 27, 17, 4]]    # stepper 5

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

def set_pins_to_output(stepperPins):
     for stepper in range (0, len(stepperPins)):
        for index in range(0, len(stepperPins[stepper])):
            GPIO.setup(stepperPins[stepper], GPIO.OUT)


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


# Initialize the Configuration of the Stepper Pins, set them to "output"
set_pins_to_output(stepperPins)


#Eingabe Schrittweite der 5 Motoren:
steps_to_perform = [0,0,0,0,0]


# Tell how it works:
print ("###### Instructions ######: \n positive number = CounterClockwise / left \n negative number = Clockwise / right")

for stepper in range(number_of_steppers):
    real_stepper_number = stepper + 1
    print "Stepper %s:" % real_stepper_number
    steps = int(raw_input("How many steps?"))
    steps_to_perform[stepper] = steps
    move_steppers(steps_to_perform)
    steps_to_perform = [0,0,0,0,0]

GPIO.cleanup()
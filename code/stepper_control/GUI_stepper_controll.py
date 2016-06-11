__author__ = 'Fabian'

import Tkinter as tk
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

delay = 0.001                   # 0.0008 seems to be the smallest possible time
number_of_steppers = 5          # maybe nr4 and nr5 need to warm up a little


# Current position of the steppers in the move-sequence: relates to MOVE_PATTERN
stepperPositions = [0, 0, 0, 0, 0]

# Pin Belegungen der 5 Motoren:
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

# Initialize the Configuration of the Stepper Pins, set them to "output"
set_pins_to_output(stepperPins)


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



class App:
    def __init__(self, master):
        frame = tk.Frame(master)
        frame.pack()
        # master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth(), master.winfo_screenheight()))

        self.button1 = tk.Button(frame, text="S1 LEFT", command=lambda: move_steppers([200, 0, 0, 0, 0]))
        self.button1.grid(row=0, column=0)
        self.button2 = tk.Button(frame, text="S1 RIGHT", command=lambda: move_steppers([-200, 0, 0, 0, 0]))
        self.button2.grid(row=0, column=1)
        self.button3 = tk.Button(frame, text="S2 LEFT", command=lambda: move_steppers([0, 200, 0, 0, 0]))
        self.button3.grid(row=1, column=0)
        self.button4 = tk.Button(frame, text="S2 RIGHT", command=lambda: move_steppers([0, -200, 0, 0, 0]))
        self.button4.grid(row=1, column=1)
        self.button5 = tk.Button(frame, text="S3 LEFT", command=lambda: move_steppers([0, 0, 200, 0, 0]))
        self.button5.grid(row=2, column=0)
        self.button6 = tk.Button(frame, text="S3 RIGHT", command=lambda: move_steppers([0, 0, -200, 0, 0]))
        self.button6.grid(row=2, column=1)
        self.button7 = tk.Button(frame, text="S4 LEFT", command=lambda: move_steppers([0, 0, 0, 200, 0]))
        self.button7.grid(row=3, column=0)
        self.button8 = tk.Button(frame, text="S4 RIGHT", command=lambda: move_steppers([0, 0, 0, -200, 0]))
        self.button8.grid(row=3, column=1)
        self.button9 = tk.Button(frame, text="S5 LEFT", command=lambda: move_steppers([0, 0, 0, 0, 200]))
        self.button9.grid(row=4, column=0)
        self.button10 = tk.Button(frame, text="S5 RIGHT", command=lambda: move_steppers([0, 0, 0, 0, -200]))
        self.button10.grid(row=4, column=1)
        self.button11 = tk.Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button11.grid(row=5, column=5)


root = tk.Tk()
app = App(root)
root.mainloop()






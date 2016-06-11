import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Pin Belegungen der 5 Motoren:

coil_A_1_pin = 6                       #Motor 1
coil_A_2_pin = 13
coil_A_3_pin = 19
coil_A_4_pin = 26

coil_B_1_pin = 12                      #Motor 2
coil_B_2_pin = 16
coil_B_3_pin = 20
coil_B_4_pin = 21

coil_C_1_pin = 14                      #Motor 3
coil_C_2_pin = 15
coil_C_3_pin = 18
coil_C_4_pin = 23

coil_D_1_pin = 24                       #Motor 4
coil_D_2_pin = 25
coil_D_3_pin = 8
coil_D_4_pin = 7

coil_E_1_pin = 4                       #Motor 5
coil_E_2_pin = 17
coil_E_3_pin = 27
coil_E_4_pin = 22

#Definiere Ausgaenge:

GPIO.setup(coil_A_1_pin, GPIO.OUT)      #Motor 1
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_A_3_pin, GPIO.OUT)
GPIO.setup(coil_A_4_pin, GPIO.OUT)

GPIO.setup(coil_B_1_pin, GPIO.OUT)      #Motor 2
GPIO.setup(coil_B_2_pin, GPIO.OUT)
GPIO.setup(coil_B_3_pin, GPIO.OUT)
GPIO.setup(coil_B_4_pin, GPIO.OUT)

GPIO.setup(coil_C_1_pin, GPIO.OUT)      #Motor 3
GPIO.setup(coil_C_2_pin, GPIO.OUT)
GPIO.setup(coil_C_3_pin, GPIO.OUT)
GPIO.setup(coil_C_4_pin, GPIO.OUT)

GPIO.setup(coil_D_1_pin, GPIO.OUT)      #Motor 4
GPIO.setup(coil_D_2_pin, GPIO.OUT)
GPIO.setup(coil_D_3_pin, GPIO.OUT)
GPIO.setup(coil_D_4_pin, GPIO.OUT)

GPIO.setup(coil_E_1_pin, GPIO.OUT)      #Motor 5
GPIO.setup(coil_E_2_pin, GPIO.OUT)
GPIO.setup(coil_E_3_pin, GPIO.OUT)
GPIO.setup(coil_E_4_pin, GPIO.OUT)

#Definiere Vorwaerts und Rueckwaerts Bewegung:

def forward(delay, steps):              #Motor 1
  for i in range(0, steps):
    setStep(1, 1, 0, 0)
    time.sleep(delay)                   #fullstepping method 512 Steps for full rotation
    setStep(0, 1, 1, 0)                 #means: 360/512=0.7degrees per Step
    time.sleep(delay)
    setStep(0, 0, 1, 1)
    time.sleep(delay)
    setStep(1, 0, 0, 1)
    time.sleep(delay)

def backwards(delay, steps):
  for i in range(0, steps):
    setStep(1, 0, 0, 1)
    time.sleep(delay)
    setStep(0, 0, 1, 1)
    time.sleep(delay)
    setStep(0, 1, 1, 0)
    time.sleep(delay)
    setStep(1, 1, 0, 0)
    time.sleep(delay)


def forward2(delay, steps2):            #Motor 2
  for i in range(0, steps2):
    setStep2(1, 1, 0, 0)
    time.sleep(delay)                   #fullstepping method 512 Steps for full rotation
    setStep2(0, 1, 1, 0)                #means: 360/512=0.7degrees per Step
    time.sleep(delay)
    setStep2(0, 0, 1, 1)
    time.sleep(delay)
    setStep2(1, 0, 0, 1)
    time.sleep(delay)

def backwards2(delay, steps2):
  for i in range(0, steps2):
    setStep2(1, 0, 0, 1)
    time.sleep(delay)
    setStep2(0, 0, 1, 1)
    time.sleep(delay)
    setStep2(0, 1, 1, 0)
    time.sleep(delay)
    setStep2(1, 1, 0, 0)
    time.sleep(delay)


def forward3(delay, steps3):            #Motor 3
  for i in range(0, steps3):
    setStep3(1, 1, 0, 0)
    time.sleep(delay)                   #fullstepping method 512 Steps for full rotation
    setStep3(0, 1, 1, 0)                #means: 360/512=0.7degrees per Step
    time.sleep(delay)
    setStep3(0, 0, 1, 1)
    time.sleep(delay)
    setStep3(1, 0, 0, 1)
    time.sleep(delay)

def backwards3(delay, steps3):
  for i in range(0, steps3):
    setStep3(1, 0, 0, 1)
    time.sleep(delay)
    setStep3(0, 0, 1, 1)
    time.sleep(delay)
    setStep3(0, 1, 1, 0)
    time.sleep(delay)
    setStep3(1, 1, 0, 0)
    time.sleep(delay)

def forward4(delay, steps4):            #Motor 4
  for i in range(0, steps4):
    setStep4(1, 1, 0, 0)
    time.sleep(delay)                   #fullstepping method 512 Steps for full rotation
    setStep4(0, 1, 1, 0)                #means: 360/512=0.7degrees per Step
    time.sleep(delay)
    setStep4(0, 0, 1, 1)
    time.sleep(delay)
    setStep4(1, 0, 0, 1)
    time.sleep(delay)

def backwards4(delay, steps4):
  for i in range(0, steps4):
    setStep4(1, 0, 0, 1)
    time.sleep(delay)
    setStep4(0, 0, 1, 1)
    time.sleep(delay)
    setStep4(0, 1, 1, 0)
    time.sleep(delay)
    setStep4(1, 1, 0, 0)
    time.sleep(delay)

def forward5(delay, steps5):            #Motor 5
  for i in range(0, steps5):
    setStep5(1, 1, 0, 0)
    time.sleep(delay)                   #fullstepping method 512 Steps for full rotation
    setStep5(0, 1, 1, 0)                #means: 360/512=0.7degrees per Step
    time.sleep(delay)
    setStep5(0, 0, 1, 1)
    time.sleep(delay)
    setStep5(1, 0, 0, 1)
    time.sleep(delay)

def backwards5(delay, steps5):
  for i in range(0, steps5):
    setStep5(1, 0, 0, 1)
    time.sleep(delay)
    setStep5(0, 0, 1, 1)
    time.sleep(delay)
    setStep5(0, 1, 1, 0)
    time.sleep(delay)
    setStep5(1, 1, 0, 0)
    time.sleep(delay)

#Definiere setStep Funktion:

def setStep(w1, w2, w3, w4):         #Motor 1
  GPIO.output(coil_A_1_pin, w1)
  GPIO.output(coil_A_2_pin, w2)
  GPIO.output(coil_A_3_pin, w3)
  GPIO.output(coil_A_4_pin, w4)

def setStep2(w1, w2, w3, w4):         #Motor 2
  GPIO.output(coil_B_1_pin, w1)
  GPIO.output(coil_B_2_pin, w2)
  GPIO.output(coil_B_3_pin, w3)
  GPIO.output(coil_B_4_pin, w4)

def setStep3(w1, w2, w3, w4):         #Motor 3
  GPIO.output(coil_C_1_pin, w1)
  GPIO.output(coil_C_2_pin, w2)
  GPIO.output(coil_C_3_pin, w3)
  GPIO.output(coil_C_4_pin, w4)

def setStep4(w1, w2, w3, w4):         #Motor 4
  GPIO.output(coil_D_1_pin, w1)
  GPIO.output(coil_D_2_pin, w2)
  GPIO.output(coil_D_3_pin, w3)
  GPIO.output(coil_D_4_pin, w4)

def setStep5(w1, w2, w3, w4):         #Motor 5
  GPIO.output(coil_E_1_pin, w1)
  GPIO.output(coil_E_2_pin, w2)
  GPIO.output(coil_E_3_pin, w3)
  GPIO.output(coil_E_4_pin, w4)


#Eingabe Schrittweite der 5 Motoren:

while True:
  setStep(0,0,0,0)
  setStep2(0,0,0,0)
  setStep3(0,0,0,0)
  setStep4(0,0,0,0)
  setStep5(0,0,0,0)
  delay = raw_input("Delay between steps (milliseconds)?")      #Delay

  steps = raw_input("Motor1: How many steps left? ")         #Motor 1 forward
  forward(int(delay) / 1000.0, int(steps))
  setStep(0,0,0,0)

  steps = raw_input("Motor1: How many steps right? ")       #Motor 1 backwards
  backwards(int(delay) / 1000.0, int(steps))
  setStep(0,0,0,0)

  steps2 = raw_input("Motor2: How many steps left? ")        #Motor 2 forward
  forward2(int(delay) / 1000.0, int(steps2))
  setStep2(0,0,0,0)

  steps2 = raw_input("Motor2: How many steps right? ")      #Motor 2 backwards
  backwards2(int(delay) / 1000.0, int(steps2))
  setStep2(0,0,0,0)

  steps3 = raw_input("Motor3: How many steps left? ")        #Motor 3 forward
  forward3(int(delay) / 1000.0, int(steps3))
  setStep3(0,0,0,0)

  steps3 = raw_input("Motor3: How many steps right? ")      #Motor 3 backwards
  backwards3(int(delay) / 1000.0, int(steps3))
  setStep3(0,0,0,0)

  steps4 = raw_input("Motor4: How many steps left? ")        #Motor 4 forward
  forward4(int(delay) / 1000.0, int(steps4))
  setStep4(0,0,0,0)

  steps4 = raw_input("Motor4: How many steps right? ")      #Motor 4 backwards
  backwards4(int(delay) / 1000.0, int(steps4))
  setStep4(0,0,0,0)

  steps5 = raw_input("Motor5: How many steps left? ")        #Motor 5 forward
  forward5(int(delay) / 1000.0, int(steps5))
  setStep5(0,0,0,0)

  steps5 = raw_input("Motor5: How many steps right? ")      #Motor 5 backwards
  backwards5(int(delay) / 1000.0, int(steps5))
  setStep5(0,0,0,0)


GPIO.cleanup()
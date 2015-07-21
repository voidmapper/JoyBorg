#!/usr/bin/env python
# coding: Latin-1

# Source: https://www.piborg.org/joyborg
# PiBorg is a trade name of Freeburn Robotics Limited.

# The software is licensed under the creative commons CC BY-NC-SA.
# http://creativecommons.org/licenses/by-nc-sa/3.0/

# https://www.piborg.org/licensing

# Modified by Glenn Powers <glenn@voidmapper.com>

## Added support for dual IBT-2/3 (Infineon BTS7960/BTN7971) H-bridge motor drivers
### L_PWM for forward, R_PWM for reverse

## Added GPIO.cleanup()

# Load library functions we want
import time
import pygame
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # Use BCM GPIO Names, see http://pi.gadgetoid.com/pinout
GPIO.setwarnings(True)

# Set which GPIO pins the drive outputs are connected to
DRIVE_1 = 24 # L FWD
DRIVE_2 = 25 # L REV
DRIVE_3 = 18 # R FWD
DRIVE_4 = 23 # R REV

# Set all of the drive pins as output pins
GPIO.setup(DRIVE_1, GPIO.OUT)
GPIO.setup(DRIVE_2, GPIO.OUT)
GPIO.setup(DRIVE_3, GPIO.OUT)
GPIO.setup(DRIVE_4, GPIO.OUT)

# Function to set all drives off
def MotorOff():
    GPIO.output(DRIVE_1, GPIO.LOW)
    GPIO.output(DRIVE_2, GPIO.LOW)
    GPIO.output(DRIVE_3, GPIO.LOW)
    GPIO.output(DRIVE_4, GPIO.LOW)
    GPIO.cleanup()

# Settings for JoyBorg
leftDrive = DRIVE_1                     # Drive number for left motor
leftReverse = DRIVE_2                     # Drive number for left motor
rightDrive = DRIVE_3                    # Drive number for right motor
rightReverse = DRIVE_4                    # Drive number for right motor
axisUpDown = 1                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 0                       # Joystick axis to read for left / right position
axisLeftRightInverted = True           # Set this to True if left and right appear to be swapped
interval = 0.1                          # Time between keyboard updates in seconds, smaller responds faster but uses more processor time
deadJoy = 0.3				# JoyStick dead zone

# Setup pygame and key states
global hadEvent
global moveUp
global moveDown
global moveLeft
global moveRight
global moveQuit
hadEvent = True
moveUp = False
moveDown = False
moveLeft = False
moveRight = False
moveQuit = False
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
screen = pygame.display.set_mode([300,300])
pygame.display.set_caption("JoyBorg - Press [ESC] to quit")

# Function to handle pygame events
def PygameHandler(events):
    # Variables accessible outside this function
    global hadEvent
    global moveUp
    global moveDown
    global moveLeft
    global moveRight
    global moveQuit
    # Handle each event individually
    for event in events:
        if event.type == pygame.QUIT:
            # User exit
            hadEvent = True
            moveQuit = True
        elif event.type == pygame.KEYDOWN:
            # A key has been pressed, see if it is one we want
            hadEvent = True
            if event.key == pygame.K_ESCAPE:
                moveQuit = True
        elif event.type == pygame.KEYUP:
            # A key has been released, see if it is one we want
            hadEvent = True
            if event.key == pygame.K_ESCAPE:
                moveQuit = False
        elif event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved, read axis positions (-1 to +1)
            hadEvent = True
            upDown = joystick.get_axis(axisUpDown)
            leftRight = joystick.get_axis(axisLeftRight)
            # Invert any axes which are incorrect
            if axisUpDownInverted:
                upDown = -upDown
            if axisLeftRightInverted:
                leftRight = -leftRight
            # Determine Up / Down values
            if upDown < (0-deadJoy):
                moveUp = True
                moveDown = False
            elif upDown > deadJoy:
                moveUp = False
                moveDown = True
            else:
                moveUp = False
                moveDown = False
            # Determine Left / Right values
            if leftRight < (0-deadJoy):
                moveLeft = True
                moveRight = False
            elif leftRight > deadJoy:
                moveLeft = False
                moveRight = True
            else:
                moveLeft = False
                moveRight = False
try:
    print 'Press [ESC] to quit'
    # Loop indefinitely
    while True:
        # Get the currently pressed keys on the keyboard
        PygameHandler(pygame.event.get())
        if hadEvent:
            # Keys have changed, generate the command list based on keys
            hadEvent = False
            if moveQuit:
                break

            elif moveLeft:
                leftState = GPIO.LOW
                leftReverseState = GPIO.LOW
                rightState = GPIO.HIGH
                rightReverseState = GPIO.LOW

            elif moveRight:
                leftState = GPIO.HIGH
                leftReverseState = GPIO.LOW
                rightState = GPIO.LOW
                rightReverseState = GPIO.LOW

            elif moveUp:
                leftState = GPIO.HIGH
                leftReverseState = GPIO.LOW
                rightState = GPIO.HIGH
                rightReverseState = GPIO.LOW

            elif moveDown:
                leftState = GPIO.LOW
                leftReverseState = GPIO.HIGH
                rightState = GPIO.LOW
                rightReverseState = GPIO.HIGH

            else:
                leftState = GPIO.LOW
                leftReverseState = GPIO.LOW
                rightState = GPIO.LOW
                rightReverseState = GPIO.LOW

            GPIO.output(leftDrive, leftState)
            GPIO.output(leftReverse, leftReverseState)
            GPIO.output(rightDrive, rightState)
            GPIO.output(rightReverse, rightReverseState)
        # Wait for the interval period
        time.sleep(interval)
    # Disable all drives
    MotorOff()
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    MotorOff()

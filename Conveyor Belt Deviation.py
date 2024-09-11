import pygame
from picamera2 import Picamera2, Preview
import time
import cv2
import numpy as np
import RPi.GPIO as gpio

# Stepper motor setup for the right motor
direction_pin_right = 20
pulse_pin_right = 21
cw_direction = 0 
ccw_direction = 1

# Stepper motor setup for the left motor
direction_pin_left = 13  
pulse_pin_left = 12     

# Setup for GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(direction_pin_right, gpio.OUT)
gpio.setup(pulse_pin_right, gpio.OUT)
gpio.setup(direction_pin_left, gpio.OUT)
gpio.setup(pulse_pin_left, gpio.OUT)

# Initialize pygame mixer
pygame.mixer.init()

# PiCamera2 setup
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 20
picam2.preview_configuration.align()
picam2.start()

fps = 0
width = 1280
height = 720
region_of_interest_vertices = [
    (0.12 * width, height),
    (0.05 * width, 0.1 * height),
    (0.96 * width, 0.1 * height),
    (0.9 * width, height)
]

# Region of Interest (ROI)
def ROI(img, vertices):
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_img = cv2.bitwise_and(img, mask)
    return masked_img

# Function for annotating the frame with the detection
def line_detected(frame, side):
    if side == "both":
        text1 = "Left Detected"
        text2 = "Right Detected"
        cv2.putText(frame, text1, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.putText(frame, text2, (900, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    elif side == "left":
        text1 = "Left detected"
        text2 = "Right not detected"
        cv2.putText(frame, text1, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.putText(frame, text2, (900, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    elif side == "right":
        text1 = "Right detected"
        text2 = "Left not detected"
        cv2.putText(frame, text1, (900, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.putText(frame, text2, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    else:
        text = "No lines detected"
        cv2.putText(frame, text, (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

# Function to rotate the right motor
def rotate_motor_right(clockwise=True):
    gpio.output(direction_pin_right, cw_direction if clockwise else ccw_direction)
    gpio.output(pulse_pin_right, gpio.HIGH)
    time.sleep(0.0001)
    gpio.output(pulse_pin_right, gpio.LOW)
    time.sleep(0.0001)

# Function to rotate the left motor
def rotate_motor_left(clockwise=True):
    gpio.output(direction_pin_left, cw_direction if clockwise else ccw_direction)
    gpio.output(pulse_pin_left, gpio.HIGH)
    time.sleep(0.0001)
    gpio.output(pulse_pin_left, gpio.LOW)
    time.sleep(0.0001)

last_detection_time = None
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output4.avi', fourcc, 5, (1280, 720))

try:
    while True:
        tStart = time.time()
        frame = picam2.capture_array()
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        crop_image = ROI(gray_image, np.array([region_of_interest_vertices], np.int32))
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
        canny_image = cv2.Canny(blurred, 170, 240)
        crop_image1 = ROI(canny_image, np.array([region_of_interest_vertices], np.int32))

        # Probabilistic Hough Transform
        lines = cv2.HoughLinesP(crop_image1, rho=1, theta=np.pi / 180, threshold=100, minLineLength=70, maxLineGap=10)

        # Calculate the vertical axis (center) of the belt
        vertical_axis = int(0.2 * width + (0.75 * width - 0.2 * width) / 2)
        result_image = frame.copy()
        # cv2.line(result_image, (vertical_axis, 0), (vertical_axis, height), (0, 255, 0), 2)
        
        # Initialize variables to the edges
        left_detected = False
        right_detected = False

        # Determining the side of line detection
        if lines is not None:
            last_detection_time = time.time()
            for line in lines:
                x1, y1, x2, y2 = line[0]
                intersection_x = (x1 + x2) // 2
                if intersection_x < vertical_axis:
                    left_detected = True
                else:
                    right_detected = True

        print("Left Detected:", left_detected)
        print("Right Detected:", right_detected)

        # Control the stepper motors based on line detection
        if left_detected and right_detected:
            print("Both lines detected.")
            line_detected(result_image, "both")
        elif left_detected:
            print("Left line detected, Right line not detected.")
            line_detected(result_image, "left")
            rotate_motor_right(clockwise=True)  # Rotate right motor clockwise
        elif right_detected:
            print("Right line detected, Left line not detected.")
            line_detected(result_image, "right")
            rotate_motor_left(clockwise=False)  # Rotate left motor counterclockwise
        else:
            print("No lines detected.")
            line_detected(result_image, "nolines")
            
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        out.write(result_image)
        fps += 1

        # Display the result image
        cv2.imshow('Frame', result_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    gpio.cleanup()
    picam2.close()
    out.release()
    cv2.destroyAllWindows()

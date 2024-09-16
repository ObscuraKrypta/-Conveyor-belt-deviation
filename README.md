# Conveyor Belt Misalignment Detection and Correction System
This project uses a Raspberry Pi and a PiCamera to detect conveyor belt misalignment and automatically correct it using stepper motors. The system utilizes OpenCV for image processing and the RPi.GPIO library to control the motors.

# Prerequisites
Before running this script, ensure you have the following hardware and software:

# Hardware
- Raspberry Pi (with GPIO capabilities)
- PiCamera
- Stepper motors (two for correction)
- Stepper motor drivers
- Conveyor belt setup with the required alignment markers

## Software:

- Python 3.x
- Required Python libraries:
  - opencv-python for image processing
  - numpy for numerical operations
  - RPi.GPIO for controlling GPIO pins on Raspberry Pi
  - pygame for audio notifications (if required)
  
## Installation
Install the required Python libraries using pip:

```sh
pip install opencv-python numpy RPi.GPIO pygame
```
## How to Use
# 1- Setup the hardware
- Connect the PiCamera, stepper motors, and the conveyor belt according to your setup requirements.
# 2- Run the script:
-  Execute the Python script on the Raspberry Pi. The script will:
   - Capture images from the PiCamera.
   - Use OpenCV to detect alignment markers on the conveyor belt.
   - Control the stepper motors to correct any detected misalignment.
- Exit:
   - To stop the program, press q on the display window.

## How It Works
1- The PiCamera captures frames of the conveyor belt.
2- The frames are processed using OpenCV to detect white lines (markers) on the conveyor belt.
3- If a misalignment is detected, the system triggers the corresponding stepper motor to correct the belt's position.
4- The system continues to monitor and correct the conveyor belt.

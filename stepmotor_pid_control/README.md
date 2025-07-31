# Step Motor PID Control

This project implements a closed-loop control system for a stepper motor using PID control based on the pixel position of a light spot detected by a camera. The system consists of several components that work together to achieve precise motor control.

## Project Structure

```
stepmotor_pid_control
├── src
│   ├── __init__.py          # Marks the src directory as a package
│   ├── motor_driver.py      # Contains the Stepmotor class for motor control
│   ├── pid_controller.py     # Implements the PIDController class for PID control
│   └── camera_control.py     # Handles camera operations and light spot detection
├── tests
│   ├── test_motor_driver.py  # Unit tests for the Stepmotor class
│   ├── test_pid_controller.py # Unit tests for the PIDController class
│   └── test_camera_control.py # Unit tests for the CameraControl class
├── requirements.txt          # Lists the required dependencies
└── README.md                 # Project documentation
```

## Installation

To install the required dependencies, run the following command:

```
pip install -r requirements.txt
```

## Usage

1. **Initialize the Camera**: Use the `CameraControl` class to set up the camera and start capturing images.
2. **Detect Light Spot**: Extract the pixel position of the light spot from the captured images.
3. **Control the Motor**: Use the `PIDController` class to calculate the control signal based on the target position and the detected position, and then send commands to the `Stepmotor` class to adjust the motor's position accordingly.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
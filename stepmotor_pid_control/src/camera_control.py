import cv2
import numpy as np
from pid_controller import PIDController

class CameraControl:
    def __init__(self, target_position, pid_kp, pid_ki, pid_kd):
        self.target_position = target_position
        self.pid_controller = PIDController(kp=pid_kp, ki=pid_ki, kd=pid_kd)
        self.cap = cv2.VideoCapture(0)  # Initialize camera

    def get_light_spot_position(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Convert to grayscale and apply threshold to find the light spot
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # Find contours of the light spot
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Assuming the largest contour is the light spot
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            if M["m00"] > 0:
                cX = int(M["m10"] / M["m00"])
                return cX  # Return the x position of the light spot
        return None

    def control_loop(self):
        while True:
            current_position = self.get_light_spot_position()
            if current_position is not None:
                control_signal = self.pid_controller.calculate(self.target_position, current_position)
                # Here you would send the control signal to the stepper motor
                print(f"Control Signal: {control_signal}")

            # Break the loop on a specific condition, e.g., a key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
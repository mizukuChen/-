import unittest
from src.camera_control import CameraControl
from src.pid_controller import PIDController

class TestCameraControl(unittest.TestCase):

    def setUp(self):
        self.camera_control = CameraControl()
        self.pid_controller = PIDController()
        self.target_position = 320  # Example target position in pixels
        self.camera_control.initialize_camera()

    def test_get_light_spot_position(self):
        position = self.camera_control.get_light_spot_position()
        self.assertIsInstance(position, tuple)
        self.assertEqual(len(position), 2)

    def test_pid_control_output(self):
        current_position = self.camera_control.get_light_spot_position()
        control_signal = self.pid_controller.calculate_control_signal(self.target_position, current_position)
        self.assertIsInstance(control_signal, float)

    def test_camera_initialization(self):
        self.assertTrue(self.camera_control.is_camera_initialized())

if __name__ == '__main__':
    unittest.main()
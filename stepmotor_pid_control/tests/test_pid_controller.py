import unittest
from src.pid_controller import PIDController

class TestPIDController(unittest.TestCase):

    def setUp(self):
        self.pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
        self.target_position = 100
        self.current_position = 90

    def test_initialization(self):
        self.assertEqual(self.pid.kp, 1.0)
        self.assertEqual(self.pid.ki, 0.1)
        self.assertEqual(self.pid.kd, 0.05)

    def test_set_gains(self):
        self.pid.set_kp(2.0)
        self.pid.set_ki(0.2)
        self.pid.set_kd(0.1)
        self.assertEqual(self.pid.kp, 2.0)
        self.assertEqual(self.pid.ki, 0.2)
        self.assertEqual(self.pid.kd, 0.1)

    def test_compute_control_signal(self):
        control_signal = self.pid.compute_control_signal(self.target_position, self.current_position)
        self.assertIsInstance(control_signal, float)

    def test_integral_and_derivative(self):
        self.pid.compute_control_signal(self.target_position, self.current_position)
        self.assertGreaterEqual(self.pid.integral, 0)
        self.assertGreaterEqual(self.pid.derivative, 0)

if __name__ == '__main__':
    unittest.main()
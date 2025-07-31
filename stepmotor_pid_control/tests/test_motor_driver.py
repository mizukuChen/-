import unittest
from unittest.mock import MagicMock
from src.motor_driver import Stepmotor

class TestStepmotor(unittest.TestCase):

    def setUp(self):
        self.uart_mock = MagicMock()
        self.motor = Stepmotor(self.uart_mock, motor_id=0)

    def test_speed_mode(self):
        self.motor.speed_mode(direction=1, speed=100)
        expected_data = bytearray([0xE0, 0xF6, 0xC8, 0xE8])
        self.uart_mock.write.assert_called_once_with(expected_data)

    def test_position_mode(self):
        self.motor.position_mode(speed=100, angle=90)
        expected_data = bytearray([0xE0, 0xFD, 0x80, 0x00, 0x00, 0x00, 0x00, 0xE8])
        self.uart_mock.write.assert_called_with(expected_data)

    def test_stop(self):
        self.motor.stop()
        expected_data = bytearray([0xE0, 0xF7, 0xE8])
        self.uart_mock.write.assert_called_once_with(expected_data)

    def test_enable(self):
        self.motor.enable(status=True)
        expected_data = bytearray([0xE0, 0xF3, 0x01, 0xE8])
        self.uart_mock.write.assert_called_once_with(expected_data)

    def test_read_encoder(self):
        self.uart_mock.read.return_value = bytearray([0xE0, 0x30, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])
        angle = self.motor.read_encoder()
        self.assertEqual(angle, 360.0 / 65536)

    def test_read_pulses(self):
        self.uart_mock.read.return_value = bytearray([0xE0, 0x33, 0x00, 0x00, 0x00, 0x01])
        pulses = self.motor.read_pulses()
        self.assertEqual(pulses, 1)

    def test_read_position(self):
        self.uart_mock.read.return_value = bytearray([0xE0, 0x36, 0x00, 0x00, 0x00, 0x01])
        position = self.motor.read_position()
        self.assertEqual(position, 360.0 / 65536)

    def test_read_error(self):
        self.uart_mock.read.return_value = bytearray([0xE0, 0x39, 0x00, 0x00])
        error = self.motor.read_error()
        self.assertEqual(error, 0.0)

    def test_reset(self):
        self.motor.reset()
        expected_data = bytearray([0xE0, 0x3F, 0xE8])
        self.uart_mock.write.assert_called_once_with(expected_data)

if __name__ == '__main__':
    unittest.main()
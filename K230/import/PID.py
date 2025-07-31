class PID:
    def __init__(self, kp, ki, kd, setpoint=0, output_limits=(None, None)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_limits = output_limits
        self._last_error = 0
        self._integral = 0

    def reset(self):
        self._last_error = 0
        self._integral = 0

    def compute(self, measurement):
        error = self.setpoint - measurement
        self._integral += error
        derivative = error - self._last_error
        output = self.kp * error + self.ki * self._integral + self.kd * derivative

        # 限制输出
        min_out, max_out = self.output_limits
        if min_out is not None:
            output = max(min_out, output)
        if max_out is not None:
            output = min(max_out, output)

        self._last_error = error
        return output
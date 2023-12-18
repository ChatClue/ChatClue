from picarx import Picarx
import threading

class PiCarXMovements:
    def __init__(self):
        self.px = Picarx()
        self.pan_angle = 0
        self.tilt_angle = 0
        self.move_timer = None

    def _set_timer(self):
        if self.move_timer is not None:
            self.move_timer.cancel()
        self.move_timer = threading.Timer(0.5, self.stop)
        self.move_timer.start()

    def move_forward(self, speed):
        self.px.set_dir_servo_angle(0)
        self.px.forward(speed)
        self._set_timer()

    def move_backward(self, speed):
        self.px.set_dir_servo_angle(0)
        self.px.backward(speed)
        self._set_timer()

    def turn_left(self, speed, angle):
        self.px.set_dir_servo_angle(-angle)
        self.px.forward(speed)
        self._set_timer()

    def turn_right(self, speed, angle):
        self.px.set_dir_servo_angle(angle)
        self.px.forward(speed)
        self._set_timer()

    def tilt_head_up(self, angle_increment):
        self.tilt_angle += angle_increment
        self.tilt_angle = min(self.tilt_angle, 35)
        self.px.set_cam_tilt_angle(self.tilt_angle)

    def tilt_head_down(self, angle_increment):
        self.tilt_angle -= angle_increment
        self.tilt_angle = max(self.tilt_angle, -35)
        self.px.set_cam_tilt_angle(self.tilt_angle)

    def turn_head_left(self, angle_increment):
        self.pan_angle -= angle_increment
        self.pan_angle = max(self.pan_angle, -35)
        self.px.set_cam_pan_angle(self.pan_angle)

    def turn_head_right(self, angle_increment):
        self.pan_angle += angle_increment
        self.pan_angle = min(self.pan_angle, 35)
        self.px.set_cam_pan_angle(self.pan_angle)

    def stop(self):
        if self.move_timer is not None:
            self.move_timer.cancel()
            self.move_timer = None
        self.px.set_dir_servo_angle(0)
        self.px.stop()

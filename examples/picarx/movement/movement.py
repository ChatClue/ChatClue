from picarx import Picarx
import threading
import time

POWER = 50
SAFE_DISTANCE = 40   # Distance in cm, > 40 is considered safe
DANGER_DISTANCE = 20 # Distance in cm, between 20 and 40 indicates caution, < 20 indicates danger

class PiCarXMovements:
    def __init__(self):
        self.px = Picarx()
        self.pan_angle = 0
        self.tilt_angle = 0
        self.move_timer = None

    def _set_timer(self, time=1.5):
        if self.move_timer is not None:
            self.move_timer.cancel()
        self.move_timer = threading.Timer(time, self.stop)
        self.move_timer.start()

    def detect_obstacle(self):
        distance = round(self.px.ultrasonic.read(), 2)
        if distance < DANGER_DISTANCE:
            return 'danger'
        elif distance < SAFE_DISTANCE:
            return 'caution'
        return 'safe'

    def move_forward(self, speed, time):
        obstacle_status = self.detect_obstacle()
        if obstacle_status == 'safe':
            self.px.set_dir_servo_angle(0)
            self.px.forward(speed)
        elif obstacle_status == 'caution':
            # Slow down and move forward cautiously
            self.px.set_dir_servo_angle(0)
            self.px.forward(speed // 2)
        else:
            # Stop in case of danger
            self.stop()
        self._set_timer(time)
    
    def turn_right(self, speed, angle, time):
        obstacle_status = self.detect_obstacle()
        if obstacle_status != 'danger':
            # Proceed with turning right
            self.px.set_dir_servo_angle(angle)
            self.px.forward(speed)
        else:
            # Stop or make a different maneuver in case of danger
            self.stop()
        self._set_timer(time)

    def turn_left(self, speed, angle, time):
        obstacle_status = self.detect_obstacle()
        if obstacle_status != 'danger':
            # Proceed with turning left
            self.px.set_dir_servo_angle(-angle)
            self.px.forward(speed)
        else:
            # Stop or make a different maneuver in case of danger
            self.stop()
        self._set_timer(time)

    def move_backward(self, speed, time):
        # Generally, we assume backward movement is a response to an obstacle in front
        self.px.set_dir_servo_angle(0)
        self.px.backward(speed)
        self._set_timer(time)
    
    def turn_left_backward(self, speed, angle, time):
        obstacle_status = self.detect_obstacle()
        if obstacle_status != 'danger':
            # Turn left while moving backward
            self.px.set_dir_servo_angle(-angle)
            self.px.backward(speed)
        else:
            # Stop in case of danger
            self.stop()
        self._set_timer(time)

    def turn_right_backward(self, speed, angle, time):
        obstacle_status = self.detect_obstacle()
        if obstacle_status != 'danger':
            # Turn right while moving backward
            self.px.set_dir_servo_angle(angle)
            self.px.backward(speed)
        else:
            # Stop in case of danger
            self.stop()
        self._set_timer(time)

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

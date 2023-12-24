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

    def move(self, direction, speed, angle, time):
        """
        Moves the car in a specified direction with a given speed, angle, and duration.
        """
        # Set the steering angle based on the input angle
        self.px.set_dir_servo_angle(angle if direction == "forward" else -angle)

        # Check for obstacles
        obstacle_status = self.detect_obstacle()

        # Determine whether to move forward or backward based on the direction and obstacle status
        if direction == "forward":
            if obstacle_status == 'safe':
                self.px.forward(speed)
            elif obstacle_status == 'caution':
                self.px.forward(speed // 2)  # Slower speed in caution state
            else:
                self.stop()  # Stop in case of danger
        elif direction == "backward":
            # Backward movement does not consider obstacles behind
            self.px.backward(speed)

        # Set a timer to stop the movement after the specified time
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

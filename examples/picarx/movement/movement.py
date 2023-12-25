from picarx import Picarx
from vilib import Vilib
import threading
import time
SAFE_DISTANCE = 40   # Distance in cm, > 40 is considered safe
DANGER_DISTANCE = 20 # Distance in cm, between 20 and 40 indicates caution, < 20 indicates danger

class PiCarXMovements:
    def __init__(self):
        self.px = Picarx()
        self.pan_angle = 0
        self.tilt_angle = 0
        self.drive_angle = 0
        self.is_moving = False
        self.is_adjusting = False
        self.move_timer = None
        self.focus_thread = None 
        self.stop_requested = False
    
    @staticmethod
    def clamp_number(num, a, b):
        return max(min(num, max(a, b)), min(a, b))

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

    def move(self, direction, speed, angle, time_to_move=0):
        """
        Moves the car in a specified direction with a given speed, angle, and duration.
        """
        self.is_moving = True
        # Adjust the steering angle based on the input angle relative to its current position
        self.drive_angle = self.clamp_number(self.drive_angle + angle, -35, 35)
        self.px.set_dir_servo_angle(self.drive_angle)

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
        if time_to_move > 0:
            self._set_timer(time_to_move)

    def move_head(self, tilt_angle, pan_angle, step=1):
        """
        Adjusts the robot's head tilt and pan angles to the specified angles.

        Args:
            tilt_angle (int): The target angle to tilt the head up/down.
            pan_angle (int): The target angle to turn the head left/right.
            step (int): The step size for each movement (default 1 degree).
        """
        target_tilt = self.clamp_number(tilt_angle, -35, 35)
        target_pan = self.clamp_number(pan_angle, -35, 35)

        # Adjust the tilt angle to the target value
        while self.tilt_angle != target_tilt:
            if self.tilt_angle < target_tilt:
                self.tilt_angle = min(self.tilt_angle + step, target_tilt)
            elif self.tilt_angle > target_tilt:
                self.tilt_angle = max(self.tilt_angle - step, target_tilt)
            self.px.set_cam_tilt_angle(self.tilt_angle)
            time.sleep(0.02)

        # Adjust the pan angle to the target value
        while self.pan_angle != target_pan:
            if self.pan_angle < target_pan:
                self.pan_angle = min(self.pan_angle + step, target_pan)
            elif self.pan_angle > target_pan:
                self.pan_angle = max(self.pan_angle - step, target_pan)
            self.px.set_cam_pan_angle(self.pan_angle)
            time.sleep(0.02)
    

    def focus_on_human(self):
        Vilib.face_detect_switch(True)
        while not self.stop_requested:
            if Vilib.detect_obj_parameter['human_n'] != 0:
                coordinate_x = Vilib.detect_obj_parameter['human_x']
                coordinate_y = Vilib.detect_obj_parameter['human_y']

                # Use clamp_number method for adjusting the pan-tilt angle
                self.pan_angle = self.clamp_number(self.pan_angle + (coordinate_x * 10 / 640) - 5, -35, 35)
                self.tilt_angle = self.clamp_number(self.tilt_angle - (coordinate_y * 10 / 480) + 5, -35, 35)
                self.px.set_cam_pan_angle(self.pan_angle)
                self.px.set_cam_tilt_angle(self.tilt_angle)
                
            time.sleep(0.05)
    
    def start_focus_on_human(self):
        """
        Starts the human focus function in a separate thread.
        """
        self.stop_requested = False
        self.focus_thread = threading.Thread(target=self.focus_on_human)
        self.focus_thread.start()

    def stop_focus_on_human(self):
        """
        Signals the human focus function to stop.
        """
        self.stop_requested = True
        if self.focus_thread.is_alive():
            self.focus_thread.join()
            Vilib.face_detect_switch(False)

    def follow_the_human(self):
        Vilib.face_detect_switch(True)
        while not self.stop_requested:
            if Vilib.detect_obj_parameter['human_n'] != 0 and not self.is_adjusting:
                coordinate_x = Vilib.detect_obj_parameter['human_x']
                # Adjust position to keep human in frame
                self.adjust_position_to_keep_human_in_frame(coordinate_x)
            time.sleep(0.05)

    def adjust_position_to_keep_human_in_frame(self, x):
        self.is_adjusting = True
        frame_center = 320  # Assuming a standard frame width of 640px
        deviation = x - frame_center

        # Continuously adjust position until deviation is within acceptable limits
        while abs(deviation) > frame_center * 0.1 and not self.is_moving:  # Adjust threshold as needed
            print(f"Adjusting position, deviation: {deviation}")
            turn_angle = -20 if deviation < 0 else 20  # Turn left for negative deviation, right for positive
            self.move("forward", 50, turn_angle)  # Continuous movement

            # Update deviation based on new human position
            if Vilib.detect_obj_parameter['human_n'] != 0:
                coordinate_x = Vilib.detect_obj_parameter['human_x']
                deviation = coordinate_x - frame_center
            else:
                pass  # Stop adjusting if human is no longer detected

            time.sleep(0.05)  # Adjust time as needed for responsiveness
        self.is_adjusting = False
        self.stop()  # Stop the car once deviation is corrected

    def start_follow_the_human(self):
        """
        Starts the human follow function in a separate thread.
        """
        self.stop_requested = False
        self.follow_thread = threading.Thread(target=self.follow_the_human)
        self.follow_thread.start()

    def stop_follow_the_human(self):
        """
        Signals the human follow function to stop.
        """
        self.stop_requested = True
        if self.follow_thread.is_alive():
            self.follow_thread.join()
            Vilib.face_detect_switch(False)

    def stop(self):
        if self.move_timer is not None:
            self.move_timer.cancel()
            self.move_timer = None
        self.px.stop()
        self.is_moving = False
    
    def reset(self):
        self.px.set_dir_servo_angle(0)
        self.px.set_cam_tilt_angle(0)
        self.px.set_cam_pan_angle(0)

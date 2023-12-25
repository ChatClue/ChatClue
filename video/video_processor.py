import cv2
import mediapipe as mp
import os
import queue
import logging
import threading
import time
from config import VIDEO_SETTINGS
from utils.os.helpers import OSHelper

class VideoProcessor:
    """
    A class to handle video processing, including capturing video input and 
    processing it with MediaPipe for pose estimation.
    """

    def __init__(self):
        # MediaPipe Pose solution initialization
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.cap = None

        # Video capture settings
        self.frame_rate = VIDEO_SETTINGS.get('FRAME_RATE', 30)
        self.device = VIDEO_SETTINGS.get('VIDEO_DEVICE', 0)
        self.capture_interval = VIDEO_SETTINGS.get('CAPTURE_INTERVAL', 2)
        self.frame_counter = 0
        self.last_capture_time = time.time()
        self.frame_queue = queue.Queue()

        # Check and create tmp directory for storing frames
        self.tmp_folder = 'tmp/video'
        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

        self.shutdown_event = threading.Event()

    def process_stream(self):
        """
        Captures and processes the video stream.
        """
        self.cap = cv2.VideoCapture(self.device)

        while not self.shutdown_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Process the frame
            self.process_frame(frame)

            # Capture frames at a set interval for saving
            if time.time() - self.last_capture_time > self.capture_interval:
                frame_name = os.path.join(self.tmp_folder, f"frame_{self.frame_counter}.jpg")
                cv2.imwrite(frame_name, frame)
                print(f"Frame saved as {frame_name}")
                self.frame_counter += 1
                self.last_capture_time = time.time()

        self.clean_up()
    
    def clean_up(self):
        """
        Releases resources and closes windows.
        """
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        OSHelper.clear_orphaned_video_files()

    def process_frame(self, frame):
        """
        Processes a single video frame.
        """
        self.frame_queue.put(frame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        if results.pose_landmarks:
            # Draw pose landmarks
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            # Additional processing can be added here
    
    def shutdown(self):
        """
        Signals the thread to terminate.
        """
        self.shutdown_event.set()
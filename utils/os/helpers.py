import os
import base64
import logging

class OSHelper:
    """
    Provides utility methods for operating system level operations, particularly file management.

    This class includes static methods for performing various file system tasks such as cleaning up orphaned files and retrieving files.
    """

    @staticmethod
    def find_closest_image(directory, target_time):
        """
        Finds the closest image file in a directory based on the target time.

        This function searches through all JPG files in the specified directory and 
        selects the one whose creation time is closest to, but not earlier than, 
        the target time.

        Args:
            directory (str): The directory path where the image files are stored.
            target_time (float): The target time (in seconds since epoch) to compare the file creation times against.

        Returns:
            str: The path of the closest image file. Returns None if no suitable file is found.
        """
        closest_file = None
        closest_time_diff = None

        # Iterate over each file in the specified directory
        for filename in os.listdir(directory):
            if filename.lower().endswith(".jpg"):  # Check if the file is a JPG image
                filepath = os.path.join(directory, filename)
                filetime = os.path.getmtime(filepath)  # Get the modification time of the file
                # Check if the file's time is later than the target time and if it's the closest so far
                if filetime > target_time:
                    logging.info(f"File is close: {filepath} - Time: {filetime}")
                    time_diff = filetime - target_time
                    if closest_time_diff is None or time_diff < closest_time_diff:
                        closest_file = filepath
                        closest_time_diff = time_diff
        return closest_file

    @staticmethod
    def convert_image_to_base64(filepath):
        """
        Converts an image file to a Base64 encoded string.

        This function reads the image file from the given filepath, encodes it in Base64,
        and then decodes it to a UTF-8 string, which can be easily used for data transfer 
        or embedding in web pages.

        Args:
            filepath (str): The path of the image file to be converted.

        Returns:
            str: The Base64 encoded string of the image.
        """
        with open(filepath, "rb") as image_file:
            # Read the file and encode it in Base64
            return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def clear_orphaned_audio_files():
        """
        Removes all audio files in a specific directory.

        This method is used to clear out any leftover audio files in the 'tmp/audio' directory. 
        It iterates through all files in the specified directory and deletes them.
        """
        # Specify the directory path for audio files
        directory_path = 'tmp/audio'

        # Iterate through and remove each file in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                os.remove(file_path)
                logging.info(f"Removed file: {file_path}")
            except OSError as e:
                logging.info(f"Error removing file {file_path}: {e}")
    
    @staticmethod
    def clear_orphaned_video_files():
        """
        Removes all video files in a specific directory.

        This method is used to clear out any leftover video files in the 'tmp/video' directory. 
        It iterates through all files in the specified directory and deletes them.
        """
        # Specify the directory path for video files
        directory_path = 'tmp/video'

        # Iterate through and remove each file in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                os.remove(file_path)
                logging.info(f"Removed file: {file_path}")
            except OSError as e:
                logging.info(f"Error removing file {file_path}: {e}")

    @staticmethod
    def system_file_cleanup():
        """
        Performs a general cleanup of system files.

        Currently, this method focuses on clearing orphaned audio files but can be expanded to include other cleanup tasks.
        """
        # Clear orphaned audio files
        OSHelper.clear_orphaned_audio_files()
        OSHelper.clear_orphaned_video_files()
    
    @staticmethod
    def configure_tmp_directories():
        """
        Ensures that the required directories (tmp/audio and tmp/video) exist.
        Creates them if they do not exist.
        """
        directories = ['tmp/audio', 'tmp/video']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Checked and ensured directory exists: {directory}")

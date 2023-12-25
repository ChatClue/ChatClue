import os

class OSHelper:
    """
    Provides utility methods for operating system level operations, particularly file management.

    This class includes static methods for performing various file system tasks such as cleaning up orphaned files.
    """

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
                print(f"Removed file: {file_path}")
            except OSError as e:
                print(f"Error removing file {file_path}: {e}")
    
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
                print(f"Removed file: {file_path}")
            except OSError as e:
                print(f"Error removing file {file_path}: {e}")

    @staticmethod
    def system_file_cleanup():
        """
        Performs a general cleanup of system files.

        Currently, this method focuses on clearing orphaned audio files but can be expanded to include other cleanup tasks.
        """
        # Clear orphaned audio files
        OSHelper.clear_orphaned_audio_files()
        OSHelper.clear_orphaned_video_files()

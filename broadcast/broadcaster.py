from config import BROADCAST_CONFIG
import importlib

class Broadcaster:
    """
    A class to manage broadcasting messages using various adapters.

    This class is responsible for initializing a broadcasting adapter based on configuration,
    sending messages through the adapter, and managing the adapter's lifecycle.

    Attributes:
        adapter: The broadcasting adapter instance used for sending messages.
    """

    def __init__(self):
        """
        Initializes the Broadcaster class by loading the adapter specified in the configuration.
        """
        # Extract the adapter path from the configuration
        adapter_path = BROADCAST_CONFIG['broadcast_adapter']
        module_name, class_name = adapter_path.rsplit(".", 1)

        # Dynamically import the module and get the adapter class
        module = importlib.import_module(module_name)
        adapter_class = getattr(module, class_name)

        # Instantiate the adapter
        self.adapter = adapter_class()

    def send_message(self, message):
        """
        Sends a message through the broadcasting adapter.

        Args:
            message: The message to be sent. Could be a string or a more complex data structure, 
                     depending on the adapter's implementation.
        """
        self.adapter.send_message(message)

    def start(self):
        """
        Starts the broadcasting adapter's process, if applicable.

        This method should be called to initialize or run any necessary processes for the adapter.
        """
        self.adapter.run()
    
    def shutdown(self):
        """
        Gracefully shuts down the broadcasting adapter, if the shutdown method is available.

        This method ensures that any resources used by the adapter are released and that the adapter
        stops its operation in a controlled manner.
        """
        if hasattr(self.adapter, 'shutdown'):
            self.adapter.shutdown()

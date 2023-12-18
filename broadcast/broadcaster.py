from config import BROADCAST_CONFIG
import importlib

class Broadcaster:
    def __init__(self):
        adapter_path = BROADCAST_CONFIG['broadcast_adapter']
        module_name, class_name = adapter_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        adapter_class = getattr(module, class_name)
        self.adapter = adapter_class()

    def send_message(self, message):
        self.adapter.send_message(message)

    def start(self):
        self.adapter.run()
    
    def shutdown(self):
        if hasattr(self.adapter, 'shutdown'):
            self.adapter.shutdown()

broadcaster = Broadcaster()
broadcaster.start()

def get_broadcaster():
    return broadcaster

import logging

# ANSI escape sequences for some colors
COLORS = {
    'WARNING': '\033[93m',  # Yellow
    'INFO': '\033[94m',     # Blue
    'DEBUG': '\033[92m',    # Green
    'CRITICAL': '\033[91m', # Red
    'ERROR': '\033[91m',    # Red
    'ENDC': '\033[0m',      # End of color
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        message = logging.Formatter.format(self, record)
        return COLORS.get(levelname, '') + message + COLORS['ENDC']
from config import AUDIO_SETTINGS

def contains_quiet_please_phrase(input_string):
    return any(phrase in input_string for phrase in AUDIO_SETTINGS['QUIET_PLEASE_PHRASES'])

def contains_wake_phrase(input_string):
    return any(phrase in input_string for phrase in AUDIO_SETTINGS['WAKE_PHRASES'])

import enum

class Events(str, enum.Enum):
    NOTIFICATION = 'notification'
    RELAY = 'relay'
    CONNECTION = 'connection'
    TERMINATION = 'termination'
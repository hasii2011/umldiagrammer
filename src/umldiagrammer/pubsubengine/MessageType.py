
from enum import Enum


class MessageType(Enum):
    DIAGRAM_SELECTION_CHANGED = 'Diagram Selection Changed'
    OPEN_PROJECT              = 'Open Project'

    NO_EVENT = 'NoEvent'

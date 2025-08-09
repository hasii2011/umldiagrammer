
from enum import Enum


class MessageType(Enum):
    UPDATE_APPLICATION_STATUS  = 'Update Application Status'
    DOCUMENT_SELECTION_CHANGED = 'Diagram Selection Changed'
    OPEN_PROJECT               = 'Open Project'
    NEW_PROJECT                = 'New Project'

    NO_EVENT = 'NoEvent'

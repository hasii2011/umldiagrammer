
from enum import Enum


class MessageType(Enum):
    UPDATE_APPLICATION_STATUS  = 'Update Application Status'
    DOCUMENT_SELECTION_CHANGED = 'Diagram Selection Changed'
    OPEN_PROJECT               = 'Open Project'
    NEW_PROJECT                = 'New Project'

    FILES_DROPPED_ON_APPLICATION = 'Files Dropped On Application'

    NO_EVENT = 'NoEvent'


from enum import Enum


class MessageType(Enum):
    UPDATE_APPLICATION_STATUS_MSG = 'Update Application Status Message'
    DOCUMENT_SELECTION_CHANGED    = 'Diagram Selection Changed'
    OPEN_PROJECT                  = 'Open Project'
    SELECT_TOOL                   = 'Select Tool'

    EDIT_CLASS                    = 'Edit Class'

    FILES_DROPPED_ON_APPLICATION   = 'Files Dropped On Application'
    OVERRIDE_PROGRAM_EXIT_POSITION = 'Override Program Exit Position'
    OVERRIDE_PROGRAM_EXIT_SIZE     = 'Override Program Exit Size'

    ACTIVE_DOCUMENT_CHANGED        = 'Active Document Changed'

    NO_EVENT = 'NoEvent'

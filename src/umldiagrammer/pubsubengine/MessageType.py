
from enum import Enum


class MessageType(Enum):
    UPDATE_APPLICATION_STATUS_MSG = 'Update Application Status Message'
    DOCUMENT_SELECTION_CHANGED    = 'Diagram Selection Changed'
    OPEN_PROJECT                  = 'Open Project'
    SELECT_TOOL                   = 'Select Tool'

    EDIT_CLASS                    = 'Edit Class'

    OVERRIDE_PROGRAM_EXIT_POSITION = 'Override Program Exit Position'
    OVERRIDE_PROGRAM_EXIT_SIZE     = 'Override Program Exit Size'

    ACTIVE_DOCUMENT_CHANGED        = 'Active Document Changed'
    GET_CURRENT_UML_PROJECT        = 'Get Current UML Project'
    CURRENT_PROJECT_SAVED          = 'Current Project Saved'
    PROJECT_RENAMED                = 'Project Renamed'
    LOLLIPOP_CREATION_REQUEST      = 'Lollipop Creation Request'

    NO_EVENT = 'NoEvent'

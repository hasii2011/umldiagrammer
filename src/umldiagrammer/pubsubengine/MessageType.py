
from enum import Enum


class MessageType(Enum):
    UPDATE_APPLICATION_STATUS_MSG = 'Update Application Status Message'
    DOCUMENT_SELECTION_CHANGED    = 'Diagram Selection Changed'
    OPEN_PROJECT                  = 'Open Project'
    CLOSE_PROJECT                 = 'Close Project'
    SAVE_PROJECT                  = 'Save Project'
    SAVE_AS_PROJECT               = 'Save as Project'
    SELECT_TOOL                   = 'Select Tool'

    EDIT_CLASS                    = 'Edit Class'

    OVERRIDE_PROGRAM_EXIT_POSITION = 'Override Program Exit Position'
    OVERRIDE_PROGRAM_EXIT_SIZE     = 'Override Program Exit Size'

    ACTIVE_DOCUMENT_CHANGED        = 'Active Document Changed'
    CURRENT_PROJECT_SAVED          = 'Current Project Saved'
    PROJECT_RENAMED                = 'Project Renamed'
    LOLLIPOP_CREATION_REQUEST      = 'Lollipop Creation Request'
    UPDATE_EDIT_MENU               = 'Update Edit Menu'

    CREATE_NEW_DIAGRAM    = 'Create New Diagram'
    #
    # This message is used by the project tree to communicate with the project panel
    # Additionally, used by the project panel to communicate to the UML Note book
    #
    DOCUMENT_NAME_CHANGED = 'Document Name Changed'

    NO_EVENT = 'NoEvent'

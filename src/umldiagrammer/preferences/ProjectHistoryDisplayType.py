
from enum import Enum

from wx import FileHistoryMenuPathStyle


class ProjectHistoryDisplayType(Enum):
    """
    Implemented so we can present easy to read values to developer
    """
    SHOW_IF_DIFFERENT = 'If Different'
    SHOW_NEVER        = 'Never'
    SHOW_ALWAYS       = 'Always'

    @classmethod
    def toWxMenuPathStyle(cls, value: 'ProjectHistoryDisplayType') -> FileHistoryMenuPathStyle:

        pathStyle: FileHistoryMenuPathStyle = FileHistoryMenuPathStyle.FH_PATH_SHOW_IF_DIFFERENT
        match value:
            case ProjectHistoryDisplayType.SHOW_IF_DIFFERENT:
                pathStyle = FileHistoryMenuPathStyle.FH_PATH_SHOW_IF_DIFFERENT
            case ProjectHistoryDisplayType.SHOW_NEVER:
                pathStyle = FileHistoryMenuPathStyle.FH_PATH_SHOW_NEVER
            case ProjectHistoryDisplayType.SHOW_ALWAYS:
                pathStyle = FileHistoryMenuPathStyle.FH_PATH_SHOW_ALWAYS
            case _:
                assert False, 'Unknown project history display type'

        return pathStyle

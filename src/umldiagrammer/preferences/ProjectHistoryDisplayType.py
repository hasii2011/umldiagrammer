
from enum import Enum

from wx import FH_PATH_SHOW_ALWAYS
from wx import FH_PATH_SHOW_IF_DIFFERENT
from wx import FH_PATH_SHOW_NEVER


class ProjectHistoryDisplayType(Enum):
    """
    Implemented so we can present easy to read values to developer
    """
    SHOW_IF_DIFFERENT = 'If Different'
    SHOW_NEVER        = 'Never'
    SHOW_ALWAYS       = 'Always'

    @classmethod
    def toWxMenuPathStyle(cls, value: 'ProjectHistoryDisplayType') -> int | None:

        pathStyle: int = FH_PATH_SHOW_IF_DIFFERENT
        match value:
            case ProjectHistoryDisplayType.SHOW_IF_DIFFERENT:
                pathStyle = FH_PATH_SHOW_IF_DIFFERENT
            case ProjectHistoryDisplayType.SHOW_NEVER:
                pathStyle = FH_PATH_SHOW_NEVER
            case ProjectHistoryDisplayType.SHOW_ALWAYS:
                pathStyle = FH_PATH_SHOW_ALWAYS
            case _:
                assert False, 'Unknown project history display type'

        return pathStyle

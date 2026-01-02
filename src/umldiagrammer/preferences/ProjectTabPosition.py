
from enum import Enum

from wx import NB_BOTTOM
from wx import NB_LEFT
from wx import NB_RIGHT
from wx import NB_TOP


class ProjectTabPosition(Enum):
    TOP     = 'Top'
    BOTTOM  = 'Bottom'
    LEFT    = 'Left'
    RIGHT   = 'Right'
    NOT_SET = 'Not Set'

    @classmethod
    def toWxNotebookPosition(cls, tabPosition: 'ProjectTabPosition') -> int:

        wxTabPosition: int = NB_TOP

        if tabPosition == ProjectTabPosition.TOP:
            wxTabPosition = NB_TOP
        elif tabPosition == ProjectTabPosition.BOTTOM:
            wxTabPosition = NB_BOTTOM
        elif tabPosition == ProjectTabPosition.LEFT:
            wxTabPosition = NB_LEFT
        elif tabPosition == ProjectTabPosition.RIGHT:
            wxTabPosition = NB_RIGHT

        return wxTabPosition

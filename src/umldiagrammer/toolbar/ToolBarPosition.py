
from enum import Enum

from wx import TB_BOTTOM
from wx import TB_LEFT
from wx import TB_RIGHT
from wx import TB_TOP


class ToolBarPosition(Enum):
    TOP     = 'Top'
    BOTTOM  = 'Bottom'
    LEFT    = 'Left'
    RIGHT   = 'Right'
    NOT_SET = 'Not Set'

    @classmethod
    def toWxPosition(cls, toolBarPosition: 'ToolBarPosition') -> int:

        wxToolBarPosition: int = TB_LEFT

        if toolBarPosition == ToolBarPosition.BOTTOM:
            wxToolBarPosition = TB_BOTTOM
        elif toolBarPosition == ToolBarPosition.TOP:
            wxToolBarPosition = TB_TOP
        elif toolBarPosition == ToolBarPosition.LEFT:
            wxToolBarPosition = TB_LEFT
        elif toolBarPosition == ToolBarPosition.RIGHT:
            wxToolBarPosition = TB_RIGHT

        return wxToolBarPosition

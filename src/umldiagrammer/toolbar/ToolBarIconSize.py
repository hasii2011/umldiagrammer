
from enum import Enum


class ToolBarIconSize(Enum):

    SMALL       = 'Small 16'
    MEDIUM      = 'Medium 24'
    LARGE       = 'Large 32'
    EXTRA_LARGE = 'Extra Large 64'

    @classmethod
    def deSerialize(cls, value: str) -> 'ToolBarIconSize':

        toolBarIconSize: ToolBarIconSize = ToolBarIconSize.LARGE

        if value == ToolBarIconSize.SMALL.value:
            toolBarIconSize = ToolBarIconSize.SMALL

        elif value == ToolBarIconSize.MEDIUM.value:
            toolBarIconSize = ToolBarIconSize.MEDIUM

        elif value == ToolBarIconSize.LARGE.value:
            toolBarIconSize = ToolBarIconSize.LARGE

        elif value == ToolBarIconSize.EXTRA_LARGE.value:
            toolBarIconSize = ToolBarIconSize.EXTRA_LARGE

        return toolBarIconSize

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

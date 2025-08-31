
from typing import Callable
from typing import NewType
from typing import cast

from enum import Enum

from dataclasses import dataclass

from wx import Bitmap
from wx import BitmapBundle

from wx import NewIdRef as wxNewIdRef


class ToolGroup(Enum):
    Menu    = 'Menu'
    Tool    = 'Tool'
    NOT_SET = 'Not Set'


@dataclass
class ToolDefinition:
    """
    Tool : A tool description for a UML Diagrammer tool
    """
    id: str = ''
    """
    A unique ID for this tool
    """
    image: BitmapBundle = cast(BitmapBundle, None)
    """
    An image for the tool
    """
    caption: str = ''
    """
    A caption for the tool
    """
    tooltip: str = ''
    """
    A tooltip: tip for this tool
    """
    toolGroup: ToolGroup = ToolGroup.NOT_SET
    """
    The tool group for this tool 
    """
    actionCallback: Callable = cast(Callable, None)
    """
    A handler method for doing this tool's actions
    """
    propertiesCallback: Callable = cast(Callable, None)
    """
    A handler function for displaying this tool's properties
    """
    wxID: int = cast(int, None)
    """
    A wx.NewIdRef
    """
    isToggle: bool = False
    """
    True if the tool can be toggled
    """

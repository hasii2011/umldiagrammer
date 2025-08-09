
from typing import Callable
from typing import NewType
from typing import cast

from dataclasses import dataclass

from wx import Bitmap
# from wx import WindowIDRef
# from wx import NewIdRef


Category       = NewType('Category',       str)


@dataclass
class Tool:
    """
    Tool : A tool description for a UML Diagrammer tool
    """
    id: str = ''
    """
    A unique ID for this tool
    """
    img: Bitmap = cast(Bitmap, None)
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
    category: Category = Category('')
    """
    A category for this tool 
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
    A wx unique ID, used for the handler
    """
    isToggle: bool = False
    """
    True if the tool can be toggled
    """

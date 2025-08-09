
# from typing import Callable
# from typing import cast

from logging import Logger
from logging import getLogger

from wx import Bitmap
from wx import EVT_TOOL
from wx import Frame
from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import NO_BORDER
from wx import TB_FLAT
from wx import TB_HORIZONTAL
from wx import ToolBar

from wx import WindowIDRef

from umldiagrammer.toolbar.Tool import Category
from umldiagrammer.toolbar.Tool import Tool
from umldiagrammer.toolbar.ToolBarIcons import ToolBarIcons

from umldiagrammer.UIIdentifiers import UIIdentifiers

TOOLS_CATEGORY: Category = Category('Pyut Tools')
MENU_CATEGORY:  Category = Category('Pyut Menu')

class ToolBarCreator:
    def __init__(self, parent: Frame):

        self._parent: Frame = parent

        self.logger: Logger = getLogger(__name__)

        self._toolBar: ToolBar = parent.CreateToolBar(TB_HORIZONTAL | NO_BORDER | TB_FLAT)

        self._createMenuTools()

        self._populateToolBar()

    @property
    def toolBar(self) -> ToolBar:
        return self._toolBar

    def _bogus(self):
        pass

    def _createMenuTools(self):

        # toolIconOwner: ToolIconOwner = self._toolIconOwner
        toolBarIcons: ToolBarIcons = ToolBarIcons()

        self._toolNewProject = Tool("diagrammer-new-project", toolBarIcons.iconNewProject,
                                    caption="New Project",
                                    tooltip="Create a new project",
                                    category=MENU_CATEGORY,
                                    actionCallback=self._bogus,
                                    wxID=UIIdentifiers.ID_FILE_MENU_NEW_PROJECT
                                    )

        # actionCallback=self._fileMenuHandler.onNewProject,

    def _populateToolBar(self):

        for tool in [self._toolNewProject]:

            if tool is not None:
                toolId:   int    = tool.wxID
                bitMap:   Bitmap = tool.img
                caption:  str    = tool.caption
                isToggle: bool   = tool.isToggle
                # noinspection PySimplifyBooleanCheck
                if isToggle is True:
                    itemKind = ITEM_CHECK
                else:
                    itemKind = ITEM_NORMAL
                """
                AddTool(toolId, label, bitmap, shortHelp=EmptyString, kind=ITEM_NORMAL) -> ToolBarToolBase
                """
                self._toolBar.AddTool(toolId=toolId, shortHelp='', bitmap=bitMap, label=caption, kind=itemKind)

                self._parent.Bind(EVT_TOOL, tool.actionCallback, id=tool.wxID)
            else:
                self._toolBar.AddSeparator()

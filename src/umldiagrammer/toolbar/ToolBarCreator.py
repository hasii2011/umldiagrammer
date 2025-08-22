
# from typing import Callable
# from typing import cast

from logging import Logger
from logging import getLogger
from typing import cast

from wx import EVT_TOOL
from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import NO_BORDER
from wx import TB_FLAT
from wx import TB_HORIZONTAL

from wx import Bitmap
from wx import BitmapBundle
from wx import Frame
from wx import TB_TEXT
from wx import ToolBar

from wx import WindowIDRef

from umldiagrammer.toolbar.ToolDefinition import ToolGroup
from umldiagrammer.toolbar.ToolDefinition import ToolDefinition
from umldiagrammer.toolbar.ToolBarIcons import ToolBarIcons

from umldiagrammer.UIIdentifiers import UIIdentifiers

NO_TOOL_DEFINITION = cast(ToolDefinition, None)


class ToolBarCreator:
    def __init__(self, parent: Frame):

        self._parent: Frame = parent

        self.logger: Logger = getLogger(__name__)

        self._toolBar: ToolBar = parent.CreateToolBar(TB_HORIZONTAL)

        self._toolNewProject:         ToolDefinition = NO_TOOL_DEFINITION
        self._toolNewClassDiagram:    ToolDefinition = NO_TOOL_DEFINITION
        self._toolNewSequenceDiagram: ToolDefinition = NO_TOOL_DEFINITION
        self._toolNewUseCaseDiagram:  ToolDefinition = NO_TOOL_DEFINITION
        self._toolOpenProject:        ToolDefinition = NO_TOOL_DEFINITION

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

        self._toolNewProject = ToolDefinition(
            "diagrammer-new-project",
            toolBarIcons.iconNewProject,
            caption="New Project",
            tooltip="Create a new project",
            toolGroup=ToolGroup.Menu,
            actionCallback=self._bogus,
            wxID=UIIdentifiers.ID_FILE_MENU_NEW_PROJECT
            )

        self._toolNewClassDiagram = ToolDefinition(
            "diagrammer-new-class-diagram",
            toolBarIcons.iconNewClassDiagram,
            caption="New Class Diagram",
            tooltip="Create an empty class diagram",
            toolGroup=ToolGroup.Menu,
            actionCallback=self._bogus,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM
        )

        self._toolNewUseCaseDiagram = ToolDefinition(
            "diagrammer-new-use-case-diagram",
            toolBarIcons.iconNewUseCaseDiagramIcon,
            caption="New Use Case Diagram",
            tooltip="Create a use case diagram",
            toolGroup=ToolGroup.Menu,
            actionCallback=self._bogus,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM
        )

        self._toolNewSequenceDiagram = ToolDefinition(
            "diagrammer-new-sequence-diagram",
            toolBarIcons.iconNewSequenceDiagramIcon,
            caption="New Class Diagram",
            tooltip="Create an sequence diagram",
            toolGroup=ToolGroup.Menu,
            actionCallback=self._bogus,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM
        )

        # actionCallback=self._fileMenuHandler.onNewProject,

    def _populateToolBar(self):

        for tool in [self._toolNewProject, self._toolNewClassDiagram, self._toolNewUseCaseDiagram, self._toolNewSequenceDiagram, None]:

            if tool is not None:
                toolId:   int    = tool.wxID
                bitMap:   Bitmap = tool.img
                caption:  str    = tool.caption
                isToggle: bool   = tool.isToggle
                toolTip:  str    = tool.tooltip

                if isToggle is True:
                    itemKind: int = ITEM_CHECK
                else:
                    itemKind = ITEM_NORMAL
                """
                AddTool(toolId, label, bitmap, shortHelp=EmptyString, kind=ITEM_NORMAL) -> ToolBarToolBase
                """
                self._toolBar.AddTool(toolId=toolId, shortHelp=toolTip, bitmap=BitmapBundle(bitMap), label=caption, kind=itemKind)

                self._parent.Bind(EVT_TOOL, tool.actionCallback, id=tool.wxID)
            else:
                self._toolBar.AddSeparator()

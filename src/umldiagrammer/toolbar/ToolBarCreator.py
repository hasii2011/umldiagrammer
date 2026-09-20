
from typing import Dict
from typing import List
from typing import cast
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import EVT_TOOL
from wx import ID_REDO
from wx import ID_UNDO
from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import ITEM_SEPARATOR
from wx import BitmapBundle
from wx import GetMousePosition
from wx import Menu
from wx import MenuItem
from wx import Point
from wx import Rect
from wx import Size

from wx.aui import AuiToolBar
from wx.aui import AuiToolBarEvent
from wx.aui import AuiToolBarItem
from wx.aui import AUI_TB_DEFAULT_STYLE
from wx.aui import AUI_TB_OVERFLOW
from wx.aui import AUI_TB_VERTICAL
from wx.aui import EVT_AUITOOLBAR_OVERFLOW_CLICK

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umldiagrammer.menuHandlers.EditMenuHandler import EditMenuHandler
from umldiagrammer.menuHandlers.FileMenuHandler import FileMenuHandler
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize
from umldiagrammer.toolbar.ToolBarIcons import IconName
from umldiagrammer.toolbar.ToolBarPosition import ToolBarPosition
from umldiagrammer.toolbar.ToolDefinition import ToolGroup
from umldiagrammer.toolbar.ToolDefinition import ToolDefinition
from umldiagrammer.toolbar.ToolBarIcons import ToolBarIcons

from umldiagrammer.UIIdentifiers import UIIdentifiers
from umldiagrammer.UIIdentifiers import UIIdentifiers as UID


NO_TOOL_DEFINITION = cast(ToolDefinition, None)

TOOL_BAR_IDs: List[int] = [
    UID.ID_ARROW,
    UID.ID_CLASS,
    UID.ID_NOTE,
    UID.ID_ACTOR,
    UID.ID_TEXT,
    UID.ID_USECASE,
    UID.ID_RELATIONSHIP_INHERITANCE, UID.ID_RELATIONSHIP_REALIZATION,
    UID.ID_RELATIONSHIP_COMPOSITION, UID.ID_RELATIONSHIP_AGGREGATION, UID.ID_RELATIONSHIP_ASSOCIATION,
    UID.ID_RELATIONSHIP_NOTE,
    UID.ID_SD_INSTANCE, UID.ID_SD_MESSAGE,
]


class ToolBarCreator:
    def __init__(self, appFrame: SizedFrame, fileMenuHandler: FileMenuHandler, editMenuHandler: EditMenuHandler, newActionCallback: Callable):

        self._appFrame: SizedFrame = appFrame

        self._fileMenuHandler:   FileMenuHandler = fileMenuHandler
        self._editMenuHandler:   EditMenuHandler = editMenuHandler
        self._newActionCallback: Callable        = newActionCallback

        self.logger: Logger = getLogger(__name__)

        self._toolBar: AuiToolBar = cast(AuiToolBar, None)

        toolBarPosition: ToolBarPosition = DiagrammerPreferences().toolBarPosition
        isVertical:      bool            = toolBarPosition in [ToolBarPosition.LEFT, ToolBarPosition.RIGHT]

        parentPanel: SizedPanel = appFrame.GetContentsPane()

        style: int = AUI_TB_DEFAULT_STYLE | AUI_TB_OVERFLOW
        if isVertical:
            style |= AUI_TB_VERTICAL

        self._toolBar = AuiToolBar(parent=parentPanel, style=style)
        self._toolBar.SetSizerProps(expand=True, proportion=0)

        #
        # Set the icon size before realizing the tool bar
        #
        self._setToolbarIconSize()

        self._toolDefinitionsById: Dict[int, ToolDefinition] = {}
        self._toolBar.Bind(EVT_AUITOOLBAR_OVERFLOW_CLICK, self._onOverflowClick)

        self._toolBarIcons: ToolBarIcons = ToolBarIcons()

        self._toolNewProject:         ToolDefinition = NO_TOOL_DEFINITION
        self._toolOpenProject:        ToolDefinition = NO_TOOL_DEFINITION
        self._toolSaveProject:        ToolDefinition = NO_TOOL_DEFINITION
        self._toolNewClassDiagram:    ToolDefinition = NO_TOOL_DEFINITION
        self._toolNewSequenceDiagram: ToolDefinition = NO_TOOL_DEFINITION
        self._toolNewUseCaseDiagram:  ToolDefinition = NO_TOOL_DEFINITION

        self._toolInheritance:     ToolDefinition = NO_TOOL_DEFINITION
        self._toolRealization:     ToolDefinition = NO_TOOL_DEFINITION
        self._toolComposition:     ToolDefinition = NO_TOOL_DEFINITION
        self._toolAggregation:     ToolDefinition = NO_TOOL_DEFINITION
        self._toolAssociation:     ToolDefinition = NO_TOOL_DEFINITION
        self._toolNoteAssociation: ToolDefinition = NO_TOOL_DEFINITION

        self._toolClass:   ToolDefinition = NO_TOOL_DEFINITION
        self._toolActor:   ToolDefinition = NO_TOOL_DEFINITION
        self._toolUseCase: ToolDefinition = NO_TOOL_DEFINITION
        self._toolNote:    ToolDefinition = NO_TOOL_DEFINITION
        self._toolText:    ToolDefinition = NO_TOOL_DEFINITION

        self._toolSDInstance: ToolDefinition = NO_TOOL_DEFINITION
        self._toolSDMessage:  ToolDefinition = NO_TOOL_DEFINITION

        self._createMenuTools()
        self._createElementTools()
        self._createRelationshipTools()
        self._populateToolBar()

    @property
    def toolBar(self) -> AuiToolBar:
        return self._toolBar

    @property
    def toolBarIds(self) -> List[int]:
        return TOOL_BAR_IDs

    def disableToolBar(self):
        self._enableToolBar(enable=False)
        self.logger.info('ToolBar disabled')

    def enableToolBar(self):
        self._enableToolBar(enable=True)
        self.logger.info('ToolBar enabled')

    def _createMenuTools(self):

        toolBarIcons: ToolBarIcons = self._toolBarIcons

        self._toolNewProject = ToolDefinition(
            id='diagrammer-new-project',
            image=toolBarIcons.getIcon(IconName.NEW_PROJECT),
            caption='New Project',
            tooltip='Create a new project',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.onNewProject,
            wxID=UIIdentifiers.ID_FILE_MENU_NEW_PROJECT,
            )

        self._toolOpenProject = ToolDefinition(
            id="diagrammer-open-project",
            image=toolBarIcons.getIcon(IconName.OPEN_PROJECT),
            caption='Open Project',
            tooltip='Open diagrammer project',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.onOpenProject,
            wxID=UIIdentifiers.ID_FILE_MENU_OPEN_PROJECT
        )
        self._toolSaveProject = ToolDefinition(
            id='diagrammer-save-project',
            image=toolBarIcons.getIcon(IconName.SAVE_PROJECT),
            caption='Save Project',
            tooltip='Save diagrammer project',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.onFileSave,
            wxID=UIIdentifiers.ID_MENU_FILE_PROJECT_SAVE
        )

        self._toolNewClassDiagram = ToolDefinition(
            id='diagrammer-new-class-diagram',
            image=toolBarIcons.getIcon(IconName.NEW_CLASS_DIAGRAM),
            caption='New Class Diagram',
            tooltip='Create an empty class diagram',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.onNewClassDiagram,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM
        )

        self._toolNewUseCaseDiagram = ToolDefinition(
            id='diagrammer-new-use-case-diagram',
            image=toolBarIcons.getIcon(IconName.NEW_USECASE_DIAGRAM),
            caption='New Use Case Diagram',
            tooltip='Create a use case diagram',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.onNewUseCaseDiagram,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM
        )

        self._toolNewSequenceDiagram = ToolDefinition(
            id='diagrammer-new-sequence-diagram',
            image=toolBarIcons.getIcon(IconName.NEW_SEQUENCE_DIAGRAM),
            caption='New Class Diagram',
            tooltip='Create an sequence diagram',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.onNewSequenceDiagram,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM
        )

        self._toolUndo = ToolDefinition(
            id='diagrammer-undo',
            image=toolBarIcons.getIcon(IconName.UNDO),
            caption="Undo",
            tooltip="Undo the last action",
            toolGroup=ToolGroup.Menu,
            actionCallback=self._editMenuHandler.onEditMenu,
            wxID=ID_UNDO
        )

        self._toolRedo = ToolDefinition(
            id='diagrammer-redo',
            image=toolBarIcons.getIcon(IconName.REDO),
            caption="Redo",
            tooltip="Redo the action",
            toolGroup=ToolGroup.Menu,
            actionCallback=self._editMenuHandler.onEditMenu,
            wxID=ID_REDO
        )

        # actionCallback=self._fileMenuHandler.onNewProject,

    def _createElementTools(self):
        toolBarIcons: ToolBarIcons = self._toolBarIcons

        self._toolArrow = ToolDefinition(
            id='diagrammer-arrow',
            image=toolBarIcons.getIcon(IconName.POINTER),
            caption="Arrow",
            tooltip="Selection tool",
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_ARROW,
            isToggle=True
        )

        self._toolClass = ToolDefinition(
            id='diagrammer-class',
            image=toolBarIcons.getIcon(IconName.CLASS),
            caption='Class',
            tooltip='Create a new class',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_CLASS,
            isToggle=True
        )

        self._toolActor = ToolDefinition(
            id='diagrammer-actor',
            image=toolBarIcons.getIcon(IconName.ACTOR),
            caption='Actor',
            tooltip='Create a new actor',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_ACTOR,
            isToggle=True
        )

        self._toolUseCase = ToolDefinition(
            id='diagrammer-use-case',
            image=toolBarIcons.getIcon(IconName.USECASE),
            caption='Use Case',
            tooltip='Create a new use case',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_USECASE,
            isToggle=True
        )

        self._toolNote = ToolDefinition(
            id='diagrammer-note',
            image=toolBarIcons.getIcon(IconName.NOTE),
            caption="Note",
            tooltip="Create a new note",
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_NOTE,
            isToggle=True
        )

        self._toolText = ToolDefinition(
            id='diagrammer-text',
            image=toolBarIcons.getIcon(IconName.TEXT),
            caption='New Text Box',
            tooltip='New Text Box',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_TEXT,
            isToggle=True
        )

    def _createRelationshipTools(self):
        toolBarIcons: ToolBarIcons = self._toolBarIcons

        self._toolInheritance = ToolDefinition(
            id='diagrammer-inheritance',
            image=toolBarIcons.getIcon(IconName.INHERITANCE),
            caption='New inheritance relation', tooltip="New inheritance relation",
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_RELATIONSHIP_INHERITANCE,
            isToggle=True
        )

        self._toolRealization = ToolDefinition(
            id='diagrammer-realization',
            image=toolBarIcons.getIcon(IconName.REALIZATION),
            caption='New Realization relation',
            tooltip='New Realization relation',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_RELATIONSHIP_REALIZATION,
            isToggle=True
        )

        self._toolComposition = ToolDefinition(
            id='umldiagrammer-composition',
            image=toolBarIcons.getIcon(IconName.COMPOSITION),
            caption='New composition relation',
            tooltip='New composition relation',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_RELATIONSHIP_COMPOSITION,
            isToggle=True
        )

        self._toolAggregation = ToolDefinition(
            id='umldiagrammer-aggregation',
            image=toolBarIcons.getIcon(IconName.AGGREGATION),
            caption='New aggregation relation',
            tooltip='New aggregation relation',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_RELATIONSHIP_AGGREGATION,
            isToggle=True
        )

        self._toolAssociation = ToolDefinition(
            id='umldiagrammer-association',
            image=toolBarIcons.getIcon(IconName.ASSOCIATION),
            caption="New association relation",
            tooltip="New association relation",
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_RELATIONSHIP_ASSOCIATION,
            isToggle=True
        )

        self._toolNoteAssociation = ToolDefinition(
            id='umldiagrammer-note-association',
            image=toolBarIcons.getIcon(IconName.NOTE_ASSOCIATION),
            caption='New note association',
            tooltip='New note association',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_RELATIONSHIP_NOTE,
            isToggle=True
        )

        self._toolSDInstance = ToolDefinition(
            id='umldiagrammer-sd-instance',
            image=toolBarIcons.getIcon(IconName.SEQUENCE_DIAGRAM_INSTANCE),
            caption='New sequence diagram instance object',
            tooltip='New sequence diagram instance object',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_SD_INSTANCE,
            isToggle=True
        )

        self._toolSDMessage = ToolDefinition(
            id='umldiagrammer-sd-message',
            image=toolBarIcons.getIcon(IconName.SEQUENCE_DIAGRAM_MESSAGE),
            caption='New sequence diagram message object',
            tooltip='New sequence diagram message object',
            toolGroup=ToolGroup.Tool,
            actionCallback=self._newActionCallback,
            wxID=UIIdentifiers.ID_SD_MESSAGE,
            isToggle=True
        )

    def _populateToolBar(self):

        for tool in [
            self._toolNewProject, self._toolOpenProject, self._toolSaveProject,
            None,
            self._toolNewClassDiagram, self._toolNewUseCaseDiagram, self._toolNewSequenceDiagram,
            None,
            self._toolArrow, self._toolUndo, self._toolRedo,
            None,
            self._toolClass, self._toolActor, self._toolUseCase, self._toolNote, self._toolText,
            self._toolInheritance, self._toolRealization, self._toolComposition, self._toolAggregation, self._toolAssociation, self._toolNoteAssociation,
            None,
            self._toolSDInstance, self._toolSDMessage
        ]:

            if tool is not None:
                toolId:   int  = tool.wxID
                caption:  str  = tool.caption
                isToggle: bool = tool.isToggle
                toolTip:  str  = tool.tooltip

                bitMapBundle: BitmapBundle = tool.image

                if isToggle is True:
                    itemKind: int = ITEM_CHECK
                else:
                    itemKind = ITEM_NORMAL
                """
                AddTool(toolId, label, bitmap, short_help_string="", kind=ITEM_NORMAL) -> AuiToolBarItem
                """
                self._toolBar.AddTool(toolId=toolId, label=caption, bitmap=bitMapBundle, short_help_string=toolTip, kind=itemKind)

                self._toolDefinitionsById[toolId] = tool
                self._appFrame.Bind(EVT_TOOL, tool.actionCallback, id=tool.wxID)
            else:
                self._toolBar.AddSeparator()

    def _setToolbarIconSize(self):
        """
        """
        preferences: DiagrammerPreferences = DiagrammerPreferences()
        if preferences.toolBarIconSize == ToolBarIconSize.SMALL:
            self._toolBar.SetToolBitmapSize(Size(16, 16))
        elif preferences.toolBarIconSize == ToolBarIconSize.MEDIUM:
            self._toolBar.SetToolBitmapSize(Size(24, 24))
        elif preferences.toolBarIconSize == ToolBarIconSize.LARGE:
            self._toolBar.SetToolBitmapSize(Size(32, 32))
        elif preferences.toolBarIconSize == ToolBarIconSize.VERY_LARGE:
            self._toolBar.SetToolBitmapSize(Size(48, 48))
        elif preferences.toolBarIconSize == ToolBarIconSize.EXTRA_LARGE:
            self._toolBar.SetToolBitmapSize(Size(64, 64))

    def _enableToolBar(self, enable: bool):
        toolBar: AuiToolBar = self._toolBar
        for toggleId in TOOL_BAR_IDs:
            toolBar.EnableTool(toolId=toggleId, state=enable)

        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_PROJECT_SAVE, state=enable)

        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM,    state=enable)
        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM,  state=enable)
        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM, state=enable)

        toolBar.EnableTool(toolId=ID_UNDO, state=enable)
        toolBar.EnableTool(toolId=ID_REDO, state=enable)

    def _onOverflowClick(self, event: AuiToolBarEvent):
        """
        Builds and displays a popup menu containing all overflowing tools when the chevron is clicked.
        """
        overflowMenu: Menu = self._buildTheOverflowMenu()
        if overflowMenu.GetMenuItemCount() > 0:
            popupPoint: Point = self._calculateOverflowPopupPoint(event)
            self._toolBar.PopupMenu(overflowMenu, popupPoint)

    def _buildTheOverflowMenu(self) -> Menu:
        """
        Builds and returns a popup menu containing all tools that
        do not fit within the visible toolbar bounds.

        The method preserveres separators,  but prevents leading separators.
        Tool toggle and enabled states are synchronized with the toolbar.
        """
        overflowMenu: Menu = Menu()
        toolCount:    int  = self._toolBar.GetToolCount()

        for idx in range(toolCount):

            if not self._toolBar.GetToolFitsByIndex(idx):
                toolItem: AuiToolBarItem = self._toolBar.FindToolByIndex(idx)
                if toolItem.GetKind() == ITEM_SEPARATOR:
                    if overflowMenu.GetMenuItemCount() > 0:
                        overflowMenu.AppendSeparator()
                else:
                    toolId: int = toolItem.GetId()
                    toolDef: ToolDefinition = self._toolDefinitionsById.get(toolId, NO_TOOL_DEFINITION)
                    if toolDef is not NO_TOOL_DEFINITION:

                        menuItemKind: int      = ITEM_CHECK if toolDef.isToggle else ITEM_NORMAL
                        menuItem:     MenuItem = MenuItem(overflowMenu, toolId, toolDef.caption, kind=menuItemKind)

                        if toolDef.image.IsOk():
                            menuItem.SetBitmap(toolDef.image)
                        overflowMenu.Append(menuItem)
                        if menuItemKind == ITEM_CHECK:
                            menuItem.Check(self._toolBar.GetToolToggled(toolId))

                        menuItem.Enable(self._toolBar.GetToolEnabled(toolId))

        return overflowMenu

    def _calculateOverflowPopupPoint(self, event: AuiToolBarEvent) -> Point:
        """
        Calculates the docking coordinates for the overflow popup menu
        adjacent to the chevron button based on toolbar orientation.
        Falls back to current mouse coordinates if chevron bounds are invalid.
        """
        buttonRect: Rect = event.GetItemRect()
        if buttonRect.IsEmpty():
            return self._toolBar.ScreenToClient(GetMousePosition())

        toolBarPosition: ToolBarPosition = DiagrammerPreferences().toolBarPosition
        popupPoint:      Point

        match toolBarPosition:
            case ToolBarPosition.TOP:
                popupPoint = Point(buttonRect.GetLeft(), buttonRect.GetBottom())
            case ToolBarPosition.BOTTOM:
                popupPoint = Point(buttonRect.GetLeft(), buttonRect.GetTop())
            case ToolBarPosition.RIGHT:
                popupPoint = Point(0, buttonRect.GetTop())
            case ToolBarPosition.LEFT:
                popupPoint = Point(self._toolBar.GetClientSize().GetWidth(), buttonRect.GetTop())
            case _:
                popupPoint = Point(buttonRect.GetLeft(), buttonRect.GetBottom())

        return popupPoint

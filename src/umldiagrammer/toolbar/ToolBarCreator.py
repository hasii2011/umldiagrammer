
from typing import Callable
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_TOOL
from wx import ID_REDO
from wx import ID_UNDO
from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import BitmapBundle
from wx import Frame
from wx import ToolBar
from wx import Size

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
    def __init__(self, appFrame: Frame, fileMenuHandler: FileMenuHandler, editMenuHandler: EditMenuHandler, newActionCallback: Callable):

        self._appFrame: Frame = appFrame

        self._fileMenuHandler:   FileMenuHandler = fileMenuHandler
        self._editMenuHandler:   EditMenuHandler = editMenuHandler
        self._newActionCallback: Callable        = newActionCallback

        self.logger: Logger = getLogger(__name__)

        wxToolBarPosition: int = ToolBarPosition.toWxPosition(DiagrammerPreferences().toolBarPosition)
        # self._toolBar: ToolBar = parent.CreateToolBar(wxToolBarPosition)
        # Manually create my own tool bar so that the icons sizes are honored
        #
        self._toolBar: ToolBar = ToolBar(parent=appFrame, style=wxToolBarPosition)

        #
        # Set the icon size before realizing the tool bar
        #
        self._setToolbarIconSize()

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

        self._appFrame.SetToolBar(self._toolBar)

    @property
    def toolBar(self) -> ToolBar:
        return self._toolBar

    @property
    def toolBarIds(self) -> List[int]:
        return TOOL_BAR_IDs

    def disableToolBar(self):
        self._enableToolBar(enable=False)

    def enableToolBar(self):
        self._enableToolBar(enable=True)

    def _createMenuTools(self):

        toolBarIcons: ToolBarIcons = self._toolBarIcons

        self._toolNewProject = ToolDefinition(
            id='diagrammer-new-project',
            image=toolBarIcons.getIcon(IconName.NEW_PROJECT),
            caption='New Project',
            tooltip='Create a new project',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.newProject,
            wxID=UIIdentifiers.ID_FILE_MENU_NEW_PROJECT,
            )

        self._toolOpenProject = ToolDefinition(
            id="diagrammer-open-project",
            image=toolBarIcons.getIcon(IconName.OPEN_PROJECT),
            caption='Open Project',
            tooltip='Open diagrammer project',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.openProject,
            wxID=UIIdentifiers.ID_FILE_MENU_OPEN_PROJECT
        )
        self._toolSaveProject = ToolDefinition(
            id='diagrammer-save-project',
            image=toolBarIcons.getIcon(IconName.SAVE_PROJECT),
            caption='Save Project',
            tooltip='Save diagrammer project',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.fileSave,
            wxID=UIIdentifiers.ID_MENU_FILE_PROJECT_SAVE
        )

        self._toolNewClassDiagram = ToolDefinition(
            id='diagrammer-new-class-diagram',
            image=toolBarIcons.getIcon(IconName.NEW_CLASS_DIAGRAM),
            caption='New Class Diagram',
            tooltip='Create an empty class diagram',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.newClassDiagram,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM
        )

        self._toolNewUseCaseDiagram = ToolDefinition(
            id='diagrammer-new-use-case-diagram',
            image=toolBarIcons.getIcon(IconName.NEW_USECASE_DIAGRAM),
            caption='New Use Case Diagram',
            tooltip='Create a use case diagram',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.newUseCaseDiagram,
            wxID=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM
        )

        self._toolNewSequenceDiagram = ToolDefinition(
            id='diagrammer-new-sequence-diagram',
            image=toolBarIcons.getIcon(IconName.NEW_SEQUENCE_DIAGRAM),
            caption='New Class Diagram',
            tooltip='Create an sequence diagram',
            toolGroup=ToolGroup.Menu,
            actionCallback=self._fileMenuHandler.newSequenceDiagram,
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
                AddTool(toolId, label, bitmap, shortHelp=EmptyString, kind=ITEM_NORMAL) -> ToolBarToolBase
                """
                self._toolBar.AddTool(toolId=toolId, shortHelp=toolTip, bitmap=bitMapBundle, label=caption, kind=itemKind)

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
        elif preferences.toolBarIconSize == ToolBarIconSize.EXTRA_LARGE:
            self._toolBar.SetToolBitmapSize(Size(64, 64))

    def _enableToolBar(self, enable: bool):
        toolBar: ToolBar = self._toolBar
        for toggleId in TOOL_BAR_IDs:
            toolBar.EnableTool(toolId=toggleId, enable=enable)

        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_PROJECT_SAVE, enable=enable)

        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM,    enable=enable)
        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM,  enable=enable)
        toolBar.EnableTool(toolId=UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM, enable=enable)

        toolBar.EnableTool(toolId=ID_UNDO, enable=enable)
        toolBar.EnableTool(toolId=ID_REDO, enable=enable)


from typing import List
from typing import NewType
from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from os import getenv as osGetEnv

from wx import BOTH
from wx import STB_DEFAULT_STYLE
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_CLOSE
from wx import FRAME_FLOAT_ON_PARENT
from wx import FRAME_TOOL_WINDOW
from wx import ID_OK

from wx import Point
from wx import Size
from wx import ToolBar
from wx import Menu
from wx import MenuBar
from wx import CommandEvent

from wx import Yield as wxYield

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from pyutmodelv2.PyutClass import PyutClass

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position
from codeallybasic.SecureConversions import SecureConversions

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.dialogs.umlclass.DlgEditClass import DlgEditClass
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import PROJECT_SUFFIX

from umldiagrammer import DiagrammerTypes
from umldiagrammer import START_STOP_MARKER

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.DiagrammerTypes import FrameIdToTitleMap
from umldiagrammer.DiagrammerTypes import HACK_ADJUST_EXIT_HEIGHT

from umldiagrammer.ActionMap import ActionMap
from umldiagrammer.UIAction import UIAction

from umldiagrammer.UIMenuCreator import UIMenuCreator
from umldiagrammer.UmlNotebook import UmlNotebook
from umldiagrammer.UmlProjectPanel import UmlProjectPanel
from umldiagrammer.actionsupervisor.ActionSupervisor import ActionSupervisor

from umldiagrammer.menuHandlers.DiagrammerFileDropTarget import DiagrammerFileDropTarget
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.pubsubengine.AppPubSubEngine import AppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

from umldiagrammer.toolbar.ToolBarCreator import ToolBarCreator

PROJECT_WILDCARD: str = f'UML Diagrammer files (*.{PROJECT_SUFFIX})|*{PROJECT_SUFFIX}'
XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'

ID_REFERENCE = NewType('ID_REFERENCE', int)


class UmlDiagrammerAppFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._preferences:    DiagrammerPreferences = DiagrammerPreferences()
        self._umlPreferences: UmlPreferences        = UmlPreferences()

        appSize: Size = Size(self._preferences.startupSize.width, self._preferences.startupSize.height)

        frameStyle:  int             = self._getFrameStyle()

        super().__init__(parent=None, title='UML Diagrammer', size=appSize, style=frameStyle)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        sizedPanel.SetSizerType('vertical')

        self._umlNotebook: UmlNotebook = cast(UmlNotebook, None)

        self._appPubSubEngine: IAppPubSubEngine = AppPubSubEngine()
        self._umlPubSubEngine: IUmlPubSubEngine  = UmlPubSubEngine()

        uiMenuCreator: UIMenuCreator = self._createApplicationMenuBar()

        self.CreateStatusBar(style=STB_DEFAULT_STYLE)  # should always do this when there's a resize border
        self.SetAutoLayout(True)

        self._toolBarCreator: ToolBarCreator = ToolBarCreator(self,
                                                              fileMenuHandler=uiMenuCreator.fileMenuHandler,
                                                              newActionCallback=self._onNewAction
                                                              )
        self._tb: ToolBar = self._toolBarCreator.toolBar
        self._tb.Realize()

        self.SetDropTarget(DiagrammerFileDropTarget(appPubSubEngine=self._appPubSubEngine, ))
        self._subscribeToMessagesWeHandle()
        self._setApplicationPosition()

        self._overrideProgramExitSize:     bool = False
        self._overrideProgramExitPosition: bool = False
        """
        The above are set to `True` by the preferences dialog when the end-user either manually specifies
        the size or position of the Pyut application.  If it is False, then normal end
        of application logic prevails;  The preferences dialog sends this class an
        event; To change the value
        """
        self._actionSupervisor: ActionSupervisor = ActionSupervisor(appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)
        self.Show(True)

        self.logger.info(f'{self._tb.GetToolSize()=}')
        self.Bind(EVT_CLOSE, self.Close)

        uiMenuCreator.helpMenuHandler.setupPubSubTracing()

    def Close(self, force: bool = False) -> bool:
        """
        Closing handler overload. Save files and ask for confirmation.

        """
        # Close all files
        # self._pyutUI.handleUnsavedProjects()
        if self._overrideProgramExitPosition is False:
            # Only save position we are not in full screen
            if self._preferences.centerAppOnStartup is False:
                x, y = self.GetPosition()
                pos: Position = Position(x=x, y=y)
                self._preferences.startupPosition = pos
                self.logger.info(f'Set new startup position: {pos}')

            # Show full screen ?
        if self._preferences.fullScreen is False:

            if self._overrideProgramExitSize is False:
                ourSize: Size = self.GetSize()

                # See issue https://github.com/hasii2011/umldiagrammer/issues/3q1
                # I need to check this on a larger monitor;
                self._preferences.startupSize = Dimensions(width=ourSize.GetWidth(), height=ourSize.GetHeight() - HACK_ADJUST_EXIT_HEIGHT)
                self.logger.info(f'Set new startup size: {ourSize}')

        self.logger.info(f'UML Diagrammer execution complete')
        self.logger.info(START_STOP_MARKER)
        self.Destroy()

        return True

    def _createApplicationMenuBar(self):

        uiMenuCreator: UIMenuCreator = UIMenuCreator(frame=self, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)
        uiMenuCreator.initializeMenus()

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = uiMenuCreator.fileMenu
        editMenu: Menu    = uiMenuCreator.editMenu
        helpMenu: Menu    = uiMenuCreator.helpMenu

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(editMenu, 'Edit')
        menuBar.Append(helpMenu, 'Help')

        self.SetMenuBar(menuBar)

        return uiMenuCreator

    def _loadProjectListener(self, umlProject: UmlProject):

        self.logger.info(f'Loading: {umlProject.fileName}')

        if self._umlNotebook is None:
            # Lazy UI creation
            # self._createTheApplicationNotebook()
            sizedPanel: SizedPanel = self.GetContentsPane()
            self._umlNotebook = UmlNotebook(sizedPanel, appPubSubEngine=self._appPubSubEngine)

        projectPanel: UmlProjectPanel = UmlProjectPanel(self._umlNotebook,
                                                        appPubSubEngine=self._appPubSubEngine,
                                                        umlPubSubEngine=self._umlPubSubEngine,
                                                        umlProject=umlProject
                                                        )
        self._umlNotebook.addProject(projectPanel=projectPanel)

        frameIdMap: FrameIdToTitleMap = projectPanel.frameIdToTitleMap

        for frameId in frameIdMap.keys():
            self._umlPubSubEngine.subscribe(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                            frameId=frameId,
                                            listener=self._updateApplicationStatusListener)
            self._umlPubSubEngine.subscribe(UmlMessageType.FRAME_MODIFIED,
                                            frameId=frameId,
                                            listener=self._frameModifiedListener)

            self._actionSupervisor.registerNewFrame(frameId=frameId)

    def _updateApplicationStatusListener(self, message: str):
        self.logger.info(f'{message=}')
        self.SetStatusText(text=message)

    def _frameModifiedListener(self, modifiedFrameId: str):
        """
        TODO: Indicate to the end-user that the currently viewable frame is
        modified or not

        Args:
            modifiedFrameId:

        """
        self.logger.info(f'Frame Modified - {modifiedFrameId=}')

    def _overrideProgramExitPositionListener(self):
        self._overrideProgramExitPosition = True

    # noinspection PyUnusedLocal
    def _onNewAction(self, event: CommandEvent):
        """
        The tool bar and associated menu selections activate this method;  The
        action map is a map of wxPython events to UI actions.  Most of the
        time actions are a 2 step process.  For example, placing a class symbol
        on the diagrammer frame.  The user selects the action.  The UI waits for
        the placement coordinate.  Then it does the placement.
        Actions are cleared if the user selects the pointer tools.  AKA, the arrow

        Args:
            event:
        """
        currentAction: UIAction = ActionMap[event.GetId()]

        self.logger.info(f'Do an action {currentAction} --- TODO')
        self._actionSupervisor.currentAction = currentAction

        self._doToolSelect(toolId=event.GetId())
        wxYield()

    def _selectToolListener(self, toolId: int):
        """
        First clean them all, then select the required one

        Args:
            toolId:  The ID of the icon to toggle
        """
        self._doToolSelect(toolId=toolId)

    def _doToolSelect(self, toolId: int):

        toolBar:    ToolBar   = self._toolBarCreator.toolBar
        toolBarIds: List[int] = self._toolBarCreator.toolBarIds

        for deselectedToolId in toolBarIds:
            toolBar.ToggleTool(deselectedToolId, False)

        toolBar.ToggleTool(toolId, True)

    def _editClassListener(self, umlFrame: ClassDiagramFrame, pyutClass: PyutClass):
        """
        This handles the case when a new UML Class is created
        TODO:  Does this really belong here

        Args:
            umlFrame:
            pyutClass:

        """
        self.logger.debug(f"Edit: {pyutClass}")

        with DlgEditClass(umlFrame, umlPubSubEngine=self._umlPubSubEngine, pyutClass=pyutClass) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlFrame.Refresh()
                umlFrame.frameModified = True

    def _setApplicationPosition(self):
        """
        Observe preferences how to set the application position
        """
        if self._preferences.centerAppOnStartup is True:
            self.Center(BOTH)  # Center on the screen
        else:
            appPosition: Position = self._preferences.startupPosition
            self.SetPosition(pt=Point(x=appPosition.x, y=appPosition.y))

    def _subscribeToMessagesWeHandle(self):

        self._appPubSubEngine.subscribe(messageType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, listener=self._loadProjectListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.SELECT_TOOL,  uniqueId=APPLICATION_FRAME_ID, listener=self._selectToolListener)

        self._appPubSubEngine.subscribe(messageType=MessageType.UPDATE_APPLICATION_STATUS_MSG,  uniqueId=APPLICATION_FRAME_ID, listener=self._updateApplicationStatusListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID, listener=self._overrideProgramExitPositionListener)

        self._appPubSubEngine.subscribe(messageType=MessageType.EDIT_CLASS, uniqueId=APPLICATION_FRAME_ID, listener=self._editClassListener)

    def _getFrameStyle(self) -> int:
        """
        wxPython 4.2.0 update:  using FRAME_TOOL_WINDOW causes the title to be above the toolbar
        in production mode use FRAME_TOOL_WINDOW

        Fixed in 4.2.3

        Returns:  An appropriate frame style
        """
        appModeStr: Optional[str] = osGetEnv(DiagrammerTypes.APP_MODE)
        if appModeStr is None:
            appMode: bool = False
        else:
            appMode = SecureConversions.secureBoolean(appModeStr)

        frameStyle: int = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        if appMode is True:
            frameStyle = frameStyle | FRAME_TOOL_WINDOW

        return frameStyle


from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from os import getenv as osGetEnv

from pyutmodelv2.PyutClass import PyutClass
from umlshapes.dialogs.umlclass.DlgEditClass import DlgEditClass
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.UmlFrame import UmlFrame
from wx import BOTH
from wx import BookCtrlEvent
from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_CLOSE
from wx import EVT_NOTEBOOK_PAGE_CHANGED
from wx import FRAME_FLOAT_ON_PARENT
from wx import FRAME_TOOL_WINDOW
from wx import GetClientDisplayRect
from wx import ID_OK

from wx import NB_LEFT
from wx import Point
from wx import Rect
from wx import STB_DEFAULT_STYLE
from wx import ScreenDC
from wx import Size

from wx import ToolBar
from wx import Menu
from wx import MenuBar
from wx import Notebook

from wx import CallLater
from wx import CallAfter
from wx import Yield as wxYield

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position
from codeallybasic.SecureConversions import SecureConversions

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlio.Reader import Reader

from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import UmlDocument
from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlDocumentType

from umldiagrammer import DiagrammerTypes
from umldiagrammer import START_STOP_MARKER

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.DiagrammerTypes import FrameIdToTitleMap
from umldiagrammer.DiagrammerTypes import HACK_ADJUST_EXIT_HEIGHT

from umldiagrammer.ActionMap import ActionMap
from umldiagrammer.UIAction import UIAction
from umldiagrammer.UIIdentifiers import UIIdentifiers

from umldiagrammer.UIMenuCreator import UIMenuCreator
from umldiagrammer.UmlProjectPanel import UmlProjectPanel
from umldiagrammer.actionsupervisor.ActionSupervisor import ActionSupervisor

from umldiagrammer.menuHandlers.DiagrammerFileDropTarget import DiagrammerFileDropTarget
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.pubsubengine.AppPubSubEngine import AppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

from umldiagrammer.toolbar.ToolBarCreator import ToolBarCreator
from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize

DEFAULT_PROJECT_TITLE: UmlDocumentTitle = UmlDocumentTitle('NewDocument')           # TODO make a preference
DEFAULT_PROJECT_PATH:  Path             = Path('newProject.udt')

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

        self._notebook: Notebook = cast(Notebook, None)

        self._openProjects:    List[UmlProject] = []
        self._appPubSubEngine: IAppPubSubEngine = AppPubSubEngine()
        self._umlPubSubEngine: UmlPubSubEngine  = UmlPubSubEngine()

        uiMenuCreator: UIMenuCreator = self._createApplicationMenuBar()

        self.CreateStatusBar(style=STB_DEFAULT_STYLE)  # should always do this when there's a resize border
        self.SetAutoLayout(True)

        self._toolBarCreator: ToolBarCreator = ToolBarCreator(self,
                                                              fileMenuHandler=uiMenuCreator.fileMenuHandler,
                                                              newActionCallback=self._onNewAction
                                                              )
        self._tb: ToolBar = self._toolBarCreator.toolBar
        #
        # Set the icon size before realizing the tool bar
        #
        self._setToolbarIconSize()
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

        CallLater(millis=100, callableObj=self.Raise)

    def _setToolbarIconSize(self):
        """
        """
        if self._preferences.toolBarIconSize == ToolBarIconSize.SMALL:
            self._tb.SetToolBitmapSize(Size(16, 16))
        elif self._preferences.toolBarIconSize == ToolBarIconSize.MEDIUM:
            self._tb.SetToolBitmapSize(Size(24, 24))
        elif self._preferences.toolBarIconSize == ToolBarIconSize.LARGE:
            self._tb.SetToolBitmapSize(Size(32, 32))
        elif self._preferences.toolBarIconSize == ToolBarIconSize.EXTRA_LARGE:
            self._tb.SetToolBitmapSize(Size(64, 64))

    def Close(self, force: bool = False):
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

                # See issue https://github.com/hasii2011/PyUt/issues/452
                # I need to check this on a larger monitor;
                # self._preferences.startupSize = Dimensions(width=ourSize.width, ourSize[1] - HACK_ADJUST_EXIT_HEIGHT)
                self._preferences.startupSize = Dimensions(width=ourSize.GetWidth(), height=ourSize.GetHeight() - HACK_ADJUST_EXIT_HEIGHT)
                self.logger.info(f'Set new startup size: {ourSize}')

        self.logger.info(f'Pyut execution complete')
        self.logger.info(START_STOP_MARKER)
        self.Destroy()

    def _createApplicationMenuBar(self):

        uiMenuCreator: UIMenuCreator = UIMenuCreator(frame=self, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)
        uiMenuCreator.initializeMenus()

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = uiMenuCreator.fileMenu

        menuBar.Append(fileMenu, 'File')

        self.SetMenuBar(menuBar)

        return uiMenuCreator

    def _newProject(self):
        if self._notebook is None:
            self._createTheApplicationNotebook()
            #
            # Create an empty project here
            #
            umlProject:  UmlProject  = UmlProject(DEFAULT_PROJECT_PATH)
            umlDocument: UmlDocument = UmlDocument(
                documentType=UmlDocumentType.CLASS_DOCUMENT,
                documentTitle=DEFAULT_PROJECT_TITLE
            )
            umlProject.umlDocuments[DEFAULT_PROJECT_TITLE] = umlDocument
            self._loadProject(umlProject=umlProject)

    def _loadProject(self, umlProject: UmlProject):

        self.logger.info(f'Loading: {umlProject.fileName}')

        if self._notebook is None:
            self._createTheApplicationNotebook()

        projectPanel: UmlProjectPanel = UmlProjectPanel(self._notebook,
                                                        appPubSubEngine=self._appPubSubEngine,
                                                        umlPubSibEngine=self._umlPubSubEngine,
                                                        umlProject=umlProject
                                                        )
        self._notebook.AddPage(page=projectPanel, text=umlProject.fileName.stem, select=True)   # TODO add an image
        self._openProjects.append(umlProject)

        frameIdMap: FrameIdToTitleMap = projectPanel.frameIdToTitleMap

        for frameId in frameIdMap.keys():
            self._umlPubSubEngine.subscribe(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                            frameId=frameId,
                                            callback=self._onUpdateApplicationStatus)
            self._actionSupervisor.registerNewFrame(frameId=frameId)

    def _createTheApplicationNotebook(self):
        """
        Lazy UI creation
        """
        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        sizedPanel.SetSizerType('vertical')

        self._notebook = Notebook(sizedPanel, style=NB_LEFT)    # TODO: should be an application preference
        self._notebook.SetSizerProps(expand=True, proportion=1)
        CallLater(millis=100, callableObj=self._notebook.PostSizeEventToParent)
        self.Bind(EVT_NOTEBOOK_PAGE_CHANGED, self._onNewProjectDisplayed)

    def _onNewProjectDisplayed(self, event: BookCtrlEvent):
        self.logger.info(f'{event.GetSelection()=} {self._notebook.GetCurrentPage()=}')

    # noinspection PyUnusedLocal
    def _onPageClosing(self, event):
        """
        Event handler that is called when a page in the notebook is closing
        """
        page = self._notebook.GetCurrentPage()
        page.Close()
        if len(self._openProjects) == 0:
            CallAfter(self._notebook.Destroy)
            self._notebook = None

    def _onLoadDroppedFile(self, filename: str):
        """
        This is the handler for the FILES_DROPPED_ON_APPLICATION topic
        TODO: This is a slight duplicated of the code in the FileMenuHandler,
        can we keep it DRY?

        Args:
            filename:  Should end with either PROJECT_SUFFIX or XML_SUFFIX
        """

        fileNamePath: Path   = Path(filename)
        suffix:       str    = fileNamePath.suffix
        reader:       Reader = Reader()
        if suffix == XML_SUFFIX:
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(fileNamePath))
            self._loadProject(umlProject)

        elif suffix == PROJECT_SUFFIX:
            umlProject = reader.readProjectFile(fileName=fileNamePath)
            self._loadProject(umlProject)

        else:
            assert False, 'We should not get files with bad suffixes'

    def _onUpdateApplicationStatus(self, message: str):
        self.logger.info(f'{message=}')
        self.SetStatusText(text=message)

    def _onOverrideProgramExitPosition(self):
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

        #
        # self._eventEngine.sendEvent(EventType.SetToolAction, action=currentAction)
        # self._doToolSelect(toolId=event.GetId())
        wxYield()

    def _onSelectTool(self, toolId: int):
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

    def _onEditClass(self, umlFrame: ClassDiagramFrame, pyutClass: PyutClass):

        # umlFrame: UmlDiagramsFrame = self._projectManager.currentFrame

        self.logger.debug(f"Edit: {pyutClass}")

        with DlgEditClass(umlFrame, eventEngine=self._umlPubSubEngine, pyutClass=pyutClass) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlFrame.Refresh()
                # Sends its own modify event

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

        self._appPubSubEngine.subscribe(messageType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, callback=self._loadProject)
        self._appPubSubEngine.subscribe(messageType=MessageType.NEW_PROJECT,  uniqueId=APPLICATION_FRAME_ID, callback=self._newProject)
        self._appPubSubEngine.subscribe(messageType=MessageType.SELECT_TOOL,  uniqueId=APPLICATION_FRAME_ID, callback=self._onSelectTool)

        self._appPubSubEngine.subscribe(messageType=MessageType.FILES_DROPPED_ON_APPLICATION,   uniqueId=APPLICATION_FRAME_ID, callback=self._onLoadDroppedFile)
        self._appPubSubEngine.subscribe(messageType=MessageType.UPDATE_APPLICATION_STATUS_MSG,  uniqueId=APPLICATION_FRAME_ID, callback=self._onUpdateApplicationStatus)
        self._appPubSubEngine.subscribe(messageType=MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID, callback=self._onOverrideProgramExitPosition)

        self._appPubSubEngine.subscribe(messageType=MessageType.EDIT_CLASS, uniqueId=APPLICATION_FRAME_ID, callback=self._onEditClass)

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

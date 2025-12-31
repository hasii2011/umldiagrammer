
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_ACTIVATE
from wx import EVT_WINDOW_DESTROY
from wx import ICON_ERROR
from wx import ID_OK
from wx import BOTH
from wx import ID_FILE1
from wx import OK
from wx import STB_DEFAULT_STYLE
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_CLOSE
from wx import FRAME_FLOAT_ON_PARENT

from wx import MessageDialog
from wx import ActivateEvent
from wx import Point
from wx import ScreenDC
from wx import Size
from wx import ToolBar
from wx import Menu
from wx import MenuBar
from wx import CommandEvent
from wx import WindowDestroyEvent

from wx import Yield as wxYield

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from umlmodel.Class import Class
from umlmodel.Note import Note
from umlmodel.Text import Text

from umlshapes.dialogs.DlgEditNote import DlgEditNote
from umlshapes.dialogs.DlgEditText import DlgEditText
from umlshapes.dialogs.umlclass.DlgEditClass import DlgEditClass

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.frames.DiagramFrame import FrameId
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import DEFAULT_PROJECT_PATH

from umlextensions.ExtensionsPubSub import ExtensionsPubSub

from umldiagrammer import START_STOP_MARKER
from umldiagrammer.DiagrammerTypes import DIAGRAMMER_IN_TEST_MODE

from umldiagrammer.ProjectHistory import ProjectHistory
from umldiagrammer.ProjectHistoryConfiguration import ProjectHistoryConfiguration

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.DiagrammerTypes import FrameIdMap
from umldiagrammer.DiagrammerTypes import HACK_ADJUST_EXIT_HEIGHT

from umldiagrammer.ActionMap import ActionMap
from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID
from umldiagrammer.UIAction import UIAction

from umldiagrammer.UIMenuCreator import UIMenuCreator
from umldiagrammer.UmlNotebook import UmlNotebook
from umldiagrammer.UmlProjectIO import UmlProjectIO
from umldiagrammer.UmlProjectPanel import UmlProjectPanel
from umldiagrammer.actionsupervisor.ActionSupervisor import ActionSupervisor

from umldiagrammer.data.LollipopCreationData import LollipopCreationData
from umldiagrammer.data.ProjectDossier import ProjectDossier

from umldiagrammer.menuHandlers.DiagrammerFileDropTarget import DiagrammerFileDropTarget
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences
from umldiagrammer.preferences.ProjectHistoryDisplayType import ProjectHistoryDisplayType

from umldiagrammer.pubsubengine.AppPubSubEngine import AppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

from umldiagrammer.toolbar.ToolBarCreator import ToolBarCreator

PROJECT_WILDCARD: str = f'UML Diagrammer files (*.{PROJECT_SUFFIX})|*{PROJECT_SUFFIX}'
XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'

ID_REFERENCE = NewType('ID_REFERENCE', int)

PROJECT_HISTORY_BASE_FILENAME: str = 'umlDiagrammerRecentProjects.ini'
VENDOR_NAME:                   str = 'ElGatoMalo'
APPLICATION_NAME:              str = 'UmlDiagrammer'


class UmlDiagrammerAppFrame(SizedFrame):
    """
    Provides two methods for the main diagram class.  Either open the last opened project
    or open an empty project

    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._preferences:    DiagrammerPreferences = DiagrammerPreferences()
        self._umlPreferences: UmlPreferences        = UmlPreferences()

        # Show full screen ?
        if self._preferences.fullScreen is True:

            dc:   ScreenDC = ScreenDC()
            appSize: Size     = dc.GetSize()

            appSize.height -= HACK_ADJUST_EXIT_HEIGHT

            super().__init__(parent=None, title='UML Diagrammer')
            self.Maximize(True)
            self.CentreOnScreen()
        else:
            appSize = Size(self._preferences.startupSize.width, self._preferences.startupSize.height)
            frameStyle: int  = self._getFrameStyle()

            super().__init__(parent=None, title='UML Diagrammer', size=appSize, style=frameStyle)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        sizedPanel.SetSizerType('vertical')

        self._umlNotebook: UmlNotebook = cast(UmlNotebook, None)

        self._appPubSubEngine: IAppPubSubEngine = AppPubSubEngine()
        self._umlPubSubEngine: IUmlPubSubEngine  = UmlPubSubEngine()

        uiMenuCreator: UIMenuCreator = self._createApplicationMenuBar()

        self._editMenu: Menu = uiMenuCreator.editMenu

        # incestuous stuff going on here !!!
        self._projectHistory: ProjectHistory = self._setupProjectHistory(fileMenu=uiMenuCreator.fileMenu)

        uiMenuCreator.fileMenuHandler.fileHistory = self._projectHistory

        self.CreateStatusBar(style=STB_DEFAULT_STYLE)  # should always do this when there's a resize border
        self.SetAutoLayout(True)

        self._toolBarCreator: ToolBarCreator = ToolBarCreator(self,
                                                              fileMenuHandler=uiMenuCreator.fileMenuHandler,
                                                              editMenuHandler=uiMenuCreator.editMenuHandler,
                                                              newActionCallback=self._onNewAction
                                                              )
        self._tb: ToolBar = self._toolBarCreator.toolBar
        self._tb.Realize()

        self.SetDropTarget(DiagrammerFileDropTarget(appPubSubEngine=self._appPubSubEngine, ))
        self._subscribeToMessagesWeHandle()
        self._setApplicationPosition()

        self._overrideProgramExitSize:     bool = False
        self._overrideProgramExitPosition: bool = False
        self._tipsAlreadyDisplayed:        bool = False
        """
        The above are set to `True` by the preferences dialog when the end-user either manually specifies
        the size or position of the Diagrammer application.  If it is False, then normal end
        of application logic prevails;  The preferences dialog sends this class an
        event; To change the value
        """
        self._actionSupervisor: ActionSupervisor = ActionSupervisor(appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)
        self.Show(True)

        self.logger.debug(f'{self._tb.GetToolSize()=}')
        self.Bind(EVT_ACTIVATE, self._onActivate)
        self.Bind(EVT_CLOSE,    self.Close)
        self.Bind(EVT_WINDOW_DESTROY, self._onWindowDestroy)

        uiMenuCreator.helpMenuHandler.setupPubSubTracing()
        self._extensionsPubSub: ExtensionsPubSub = uiMenuCreator.extensionsMenuHandler.extensionsPubSub

        self._uiMenuCreator: UIMenuCreator = uiMenuCreator
        self._setTestItems()

    def Close(self, force: bool = False) -> bool:
        """
        Closing handler overload. Save files and ask for confirmation.
        """
        # Close all files
        if self._umlNotebook is not None:
            self._umlNotebook.handleUnsavedProjects()
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

        #
        # Cleanup in case we were running in test mode
        #
        DIAGRAMMER_IN_TEST_MODE.unlink(missing_ok=True)

        return True

    def loadProjectByFilename(self, fileName: str):
        """
        Used by the App when MAC OS passes file names

        Args:
            fileName:
        """
        self._loadProjectByName(fileName=fileName)

    def loadLastOpenedProject(self):

        lastOpenFileName: str = self._projectHistory.GetHistoryFile(0)
        self._loadProjectByName(fileName=lastOpenFileName)

    def loadEmptyProject(self):
        umlProject: UmlProject = UmlProject.emptyProject()
        self._displayProject(umlProject=umlProject)

    def _loadProjectByName(self, fileName: str):
        """
        DRY
        Args:
            fileName:   File name to open
        """
        umlProjectIO: UmlProjectIO = UmlProjectIO(appPubSubEngine=self._appPubSubEngine)
        umlProject:   UmlProject   = umlProjectIO.readProject(fileToOpen=fileName)

        self._displayProject(umlProject=umlProject)

    def _createApplicationMenuBar(self):

        uiMenuCreator: UIMenuCreator = UIMenuCreator(frame=self, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)

        menuBar:        MenuBar = MenuBar()
        fileMenu:       Menu    = uiMenuCreator.fileMenu
        editMenu:       Menu    = uiMenuCreator.editMenu
        extensionsMenu: Menu    = uiMenuCreator.extensionsMenu
        helpMenu:       Menu    = uiMenuCreator.helpMenu

        menuBar.Append(fileMenu,       'File')
        menuBar.Append(editMenu,       'Edit')
        menuBar.Append(extensionsMenu, 'Extensions')
        menuBar.Append(helpMenu,       'Help')

        self.SetMenuBar(menuBar)

        return uiMenuCreator

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

        self.logger.debug(f'Do an action {currentAction} --- TODO')
        self._actionSupervisor.currentAction = currentAction

        self._doToolSelect(toolId=event.GetId())
        wxYield()

    # noinspection PyUnusedLocal
    def _onWindowDestroy(self, event: WindowDestroyEvent):
        """
        TODO: Maybe this belongs in the Close handler
        A little extra cleanup is required for the FileHistory control;
        Take time to persist the file history
        Args:
            event:
        """
        #
        # On OS X this gets stored in ~/Library/Preferences
        # Nothing I did to the FileHistoryConfiguration object seemed to change that
        projectHistoryConfiguration: ProjectHistoryConfiguration = ProjectHistoryConfiguration(appName=APPLICATION_NAME,
                                                                                               vendorName=VENDOR_NAME,
                                                                                               localFilename=PROJECT_HISTORY_BASE_FILENAME)

        self._projectHistory.Save(projectHistoryConfiguration)

    def _onActivate(self, event: ActivateEvent):
        """
        EVT_ACTIVATE Callback; display tips frame.
        But only on the first activation
        TODO: This belongs somewhere else

        Args:
            event:
        """
        self.logger.debug(f'_onActivate event: {event.GetActive()=}')
        if self._tipsAlreadyDisplayed is True:
            pass
        else:
            self.logger.debug(f'Displaying Tips is not yet implemented')
            #     # Display tips frame
            #     prefs: DiagrammerPreferences = DiagrammerPreferences()
            #     self.logger.debug(f'Show tips on startup: {self._prefs.showTipsOnStartup=}')
            #     if prefs.showTipsOnStartup is True:
            #         # noinspection PyUnusedLocal
            #         tipsFrame: DlgTipsV2 = DlgTipsV2(self)
            #         tipsFrame.Show(show=True)
            self._tipsAlreadyDisplayed = True

    def _selectToolListener(self, toolId: int):
        """
        First clean them all, then select the required one

        Args:
            toolId:  The ID of the icon to toggle
        """
        self._doToolSelect(toolId=toolId)

    def _editClassListener(self, umlFrame: ClassDiagramFrame, modelClass: Class):
        """
        This handles the case when a new UML Class is created
        TODO:  Does this really belong here

        Args:
            umlFrame:
            modelClass:

        """
        self.logger.debug(f"Edit: {modelClass}")

        with DlgEditClass(umlFrame, umlPubSubEngine=self._umlPubSubEngine, modelClass=modelClass) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlFrame.Refresh()
                umlFrame.frameModified = True

    def _editNoteListener(self, umlFrame: ClassDiagramFrame, note: Note):
        """
        This handles the case when a new UML Note is created
        TODO:  Does this really belong here

        Args:
            umlFrame:
            note:
        """
        with DlgEditNote(umlFrame, note=note) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlFrame.Refresh()
                umlFrame.frameModified = True

    def _editTextListener(self, umlFrame: ClassDiagramFrame, text: Text):
        """
        This handles the case when a new UML Text is created
        TODO:  Does this really belong here

        Args:
            umlFrame:
            text:

        """
        with DlgEditText(umlFrame, text=text) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlFrame.Refresh()
                umlFrame.frameModified = True

    def _openProjectListener(self, umlProject: UmlProject):
        self._displayProject(umlProject=umlProject)
        #
        # Blindly re-enable if we open more than 1 project
        #
        self._toolBarCreator.enableToolBar()
        self._uiMenuCreator.enableMenus()

    def _saveProjectListener(self):
        """
        Saves the current project
        """
        projectDossier: ProjectDossier = self._umlNotebook.currentProject
        umlProject:     UmlProject     = projectDossier.umlProject

        umlProjectIO:   UmlProjectIO   = UmlProjectIO(appPubSubEngine=self._appPubSubEngine)

        if umlProject.fileName == DEFAULT_PROJECT_PATH:
            umlProjectIO.doFileSaveAs(umlProject=projectDossier.umlProject)
        else:
            if projectDossier.modified is True:
                umlProjectIO.saveProject(umlProject=umlProject)

                self._appPubSubEngine.sendMessage(messageType=MessageType.CURRENT_PROJECT_SAVED,
                                                  uniqueId=NOTEBOOK_ID,
                                                  projectPath=umlProject.fileName
                                                  )
            else:
                self.SetStatusText(text='No save needed, project not modified')

    def _saveNamedProjectListener(self, umlProject: UmlProject):

        umlProjectIO:   UmlProjectIO   = UmlProjectIO(appPubSubEngine=self._appPubSubEngine)

        if umlProject.fileName == DEFAULT_PROJECT_PATH:
            projectName: str = umlProjectIO.doFileSaveAs(umlProject=umlProject)
        else:
            umlProjectIO.saveProject(umlProject=umlProject)
            projectName = str(umlProject.fileName)

        self._projectHistory.AddFileToHistory(projectName)

    def _saveAsProjectListener(self):
        """
        Save As the current project
        """
        projectDossier: ProjectDossier = self._umlNotebook.currentProject

        if projectDossier.umlProject is None:
            booBoo: MessageDialog = MessageDialog(parent=None, message='No UML documents to save !', caption='Error', style=OK | ICON_ERROR)
            booBoo.ShowModal()
        else:
            umlProjectIO: UmlProjectIO = UmlProjectIO(appPubSubEngine=self._appPubSubEngine)
            umlProjectIO.doFileSaveAs(umlProject=projectDossier.umlProject)
            self._projectHistory.AddFileToHistory(filename=str(projectDossier.umlProject.fileName))

    def _updateApplicationStatusListener(self, message: str):
        self.logger.debug(f'{message=}')
        self.SetStatusText(message)

    def _overrideProgramExitPositionListener(self):
        self._overrideProgramExitPosition = True

    def _lollipopCreationRequestListener(self, lollipopCreationData: LollipopCreationData):
        self._actionSupervisor.createLollipopInterface(lollipopCreationData=lollipopCreationData)

    def _noOpenProjectsListener(self):
        self._toolBarCreator.disableToolBar()
        self._uiMenuCreator.disableMenus()

    def _registerNewFrameListener(self, frameId: FrameId):
        self._doRegistration(frameId=frameId)

    def _subscribeToMessagesWeHandle(self):

        self._appPubSubEngine.subscribe(messageType=MessageType.OPEN_PROJECT,    uniqueId=APPLICATION_FRAME_ID, listener=self._openProjectListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.SAVE_PROJECT,    uniqueId=APPLICATION_FRAME_ID, listener=self._saveProjectListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.SAVE_AS_PROJECT, uniqueId=APPLICATION_FRAME_ID, listener=self._saveAsProjectListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.SELECT_TOOL,     uniqueId=APPLICATION_FRAME_ID, listener=self._selectToolListener)

        self._appPubSubEngine.subscribe(messageType=MessageType.UPDATE_APPLICATION_STATUS_MSG,  uniqueId=APPLICATION_FRAME_ID, listener=self._updateApplicationStatusListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID, listener=self._overrideProgramExitPositionListener)

        self._appPubSubEngine.subscribe(messageType=MessageType.EDIT_CLASS, uniqueId=APPLICATION_FRAME_ID, listener=self._editClassListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.EDIT_NOTE,  uniqueId=APPLICATION_FRAME_ID, listener=self._editNoteListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.EDIT_TEXT,  uniqueId=APPLICATION_FRAME_ID, listener=self._editTextListener)

        self._appPubSubEngine.subscribe(messageType=MessageType.LOLLIPOP_CREATION_REQUEST, uniqueId=APPLICATION_FRAME_ID, listener=self._lollipopCreationRequestListener)

        self._appPubSubEngine.subscribe(messageType=MessageType.REGISTER_NEW_FRAME, uniqueId=APPLICATION_FRAME_ID, listener=self._registerNewFrameListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.SAVE_NAMED_PROJECT, uniqueId=APPLICATION_FRAME_ID, listener=self._saveNamedProjectListener)
        self._appPubSubEngine.subscribe(messageType=MessageType.NO_OPEN_PROJECTS,   uniqueId=APPLICATION_FRAME_ID, listener=self._noOpenProjectsListener)

    def _getFrameStyle(self) -> int:
        """
        wxPython 4.2.4 update:  using FRAME_TOOL_WINDOW causes the title to be above the toolbar
        in production mode use FRAME_TOOL_WINDOW

        Note:  Getting the environment variable from the plist dictionary (LSEnvironment) only works
        by double-clicking on the built application;  We simulate that with a PyCharm custom Run/Debug
        configuration

        Returns:  An appropriate frame style
        """
        # appModeStr: Optional[str] = osGetEnv(DiagrammerTypes.APP_MODE)

        # if appModeStr is None:
        #     appMode: bool = False
        # else:
        #     appMode = SecureConversions.secureBoolean(appModeStr)
        frameStyle: int  = DEFAULT_FRAME_STYLE
        # if appMode is True:
        #     frameStyle = frameStyle | FRAME_TOOL_WINDOW

        return frameStyle

    def _setupProjectHistory(self, fileMenu: Menu) -> ProjectHistory:
        """
        The file is at ~/Library/Preferences/umlDiagrammerRecentProjects.ini
        Args:
            fileMenu: The file menu object

        Returns:  A FileHistory object
        """
        projectHistory: ProjectHistory = ProjectHistory(idBase=ID_FILE1)
        fhStyle:     int | None  = ProjectHistoryDisplayType.toWxMenuPathStyle(self._preferences.fileHistoryDisplay)
        projectHistory.SetMenuPathStyle(style=fhStyle)

        fileHistoryConfiguration: ProjectHistoryConfiguration = ProjectHistoryConfiguration(appName=APPLICATION_NAME,
                                                                                            vendorName=VENDOR_NAME,
                                                                                            localFilename=PROJECT_HISTORY_BASE_FILENAME)

        projectHistory.UseMenu(fileMenu)
        projectHistory.Load(fileHistoryConfiguration)

        self.logger.debug(f'{fileHistoryConfiguration.GetPath()=}')

        return projectHistory

    def _setApplicationPosition(self):
        """
        Observe preferences how to set the application position

        """
        if self._preferences.fullScreen is False:
            if self._preferences.centerAppOnStartup is True:
                self.Center(BOTH)  # Center on the screen
            else:
                appPosition: Position = self._preferences.startupPosition
                self.SetPosition(pt=Point(x=appPosition.x, y=appPosition.y))

    def _doToolSelect(self, toolId: int):

        toolBar:    ToolBar   = self._toolBarCreator.toolBar
        toolBarIds: List[int] = self._toolBarCreator.toolBarIds

        for deselectedToolId in toolBarIds:
            toolBar.ToggleTool(deselectedToolId, False)

        toolBar.ToggleTool(toolId, True)

    def _displayProject(self, umlProject: UmlProject):
        """
        This methods takes the UML project and displays it in the UI.  As a
        side affect (bad) adds the file name to the fileHistory

        Args:
            umlProject:  The project to display in the UI

        """
        self.logger.info(f'Displaying: {umlProject.fileName}')

        if self._umlNotebook is None:
            # Lazy UI creation

            sizedPanel: SizedPanel = self.GetContentsPane()
            self._umlNotebook = UmlNotebook(sizedPanel,
                                            appPubSubEngine=self._appPubSubEngine,
                                            umlPubSubEngine=self._umlPubSubEngine,
                                            extensionsPubSub=self._extensionsPubSub
                                            )

        self._umlNotebook.closeDefaultProject()
        projectPanel: UmlProjectPanel = UmlProjectPanel(self._umlNotebook,
                                                        appPubSubEngine=self._appPubSubEngine,
                                                        umlPubSubEngine=self._umlPubSubEngine,
                                                        umlProject=umlProject,
                                                        editMenu=self._editMenu
                                                        )
        self._umlNotebook.addProject(projectPanel=projectPanel)

        frameIdMap: FrameIdMap = projectPanel.frameIdMap

        for frameId in frameIdMap.keys():
            self._doRegistration(frameId)

        if umlProject.fileName != DEFAULT_PROJECT_PATH:
            self._projectHistory.AddFileToHistory(filename=str(umlProject.fileName))

    def _doRegistration(self, frameId):
        """
        Get notified when s frame asks us to update the application status
        The action supervisor handles other relevant messages.  See that method

        Args:
            frameId:
        """

        self._umlPubSubEngine.subscribe(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                        frameId=frameId,
                                        listener=self._updateApplicationStatusListener)

        self._actionSupervisor.registerNewFrame(frameId=frameId)

    def _setTestItems(self):
        """
        If we are in test mode:

        * Override user application positioning
        * Set the running indicator file

        """
        from pathlib import Path
        if self._preferences.inTestMode is True:
            testPosition: Position   = self._preferences.testPosition
            testSize:     Dimensions = self._preferences.testSize

            self.SetPosition(pt=Point(x=testPosition.x, y=testPosition.y))
            self.SetSize(width=testSize.width, height=testSize.height)

            iAmRunningPath: Path = Path(DIAGRAMMER_IN_TEST_MODE)
            iAmRunningPath.touch()

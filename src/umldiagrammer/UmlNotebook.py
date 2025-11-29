
from typing import List
from typing import NewType
from typing import cast
from typing import Callable

from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import NB_LEFT
from wx import ID_YES
from wx import YES_NO
from wx import ICON_QUESTION
from wx import EVT_NOTEBOOK_PAGE_CHANGED

from wx import Notebook
from wx import BookCtrlEvent
from wx import MessageDialog
from wx import Size

from wx import CallLater

from wx.lib.sized_controls import SizedPanel

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlio.IOTypes import UmlDocumentType
from umlio.IOTypes import DEFAULT_PROJECT_PATH

from umlextensions.ExtensionsPubSub import ExtensionsMessageType
from umlextensions.ExtensionsPubSub import ExtensionsPubSub
from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsTypes import FrameSize

from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID
from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID
from umldiagrammer.DiagrammerTypes import UmlLinkGenre
from umldiagrammer.DiagrammerTypes import UmlShapeGenre

from umldiagrammer.UmlProjectIO import UmlProjectIO

from umldiagrammer.UmlProjectPanel import UmlProjectPanel
from umldiagrammer.data.ProjectDossier import ProjectDossier

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


PathList = NewType('PathList', List[Path])

OpenProjectsCallback = Callable[[PathList], None]

MODIFIED_INDICATOR: str = '*'

class UmlNotebook(Notebook):
    """
    Our own version of a notebook.  Essentially, we need to keep track when the notebook page selection
    changes.  This includes when we add new project tabs

    Project Names are just the project file name with the suffix (aka, just the stem)

    """
    def __init__(self, sizedPanel: SizedPanel, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine, extensionsPubSub: ExtensionsPubSub):
        """
        Manages Project Panels

        Args:
            sizedPanel:
            appPubSubEngine:
            umlPubSubEngine:
            extensionsPubSub:
        """

        self.logger:            Logger           = getLogger(__name__)
        self._appPubSubEngine:  IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine:  IUmlPubSubEngine = umlPubSubEngine
        self._extensionsPubSub: ExtensionsPubSub = extensionsPubSub

        super().__init__(sizedPanel, style=NB_LEFT)  # TODO: should be an application preference

        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self.Bind(EVT_NOTEBOOK_PAGE_CHANGED, self._onNewProjectDisplayed)

        CallLater(millis=100, callableObj=self.PostSizeEventToParent)
        self._subscribeToApplicationMessages()
        self._subscribeToExtensionsMessages()

    @property
    def currentProject(self) -> ProjectDossier:

        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())

        return ProjectDossier(
            umlProject=projectPanel.umlProject,
            modified=projectPanel.umlProjectModified
        )

    def closeDefaultProject(self) -> bool:
        """
        Will close it if it is open

        Returns:  `True` if it was closed, else `False`
        """
        answer: bool = False

        projectCount: int = self.GetPageCount()

        for idx in range(projectCount):
            projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetPage(idx))
            if projectPanel.umlProject.fileName == DEFAULT_PROJECT_PATH:
                answer = True
                self._closeProject(projectPanel=projectPanel)
                break

        return answer

    def addProject(self, projectPanel: UmlProjectPanel):
        """
        Use this method to add a notebook page;  Do not use .AddPage directly
        Do not need to send the ACTIVE_DOCUMENT_CHANGED message since the UI
        fires a BookCtrlEvent, which we handle and fire the message there
        Args:
            projectPanel:
        """
        for frameId in projectPanel.frameIdMap.keys():
            self._umlPubSubEngine.subscribe(messageType=UmlMessageType.FRAME_MODIFIED, frameId=frameId, listener=self._frameModifiedListener)

        self.AddPage(page=projectPanel, text=projectPanel.umlProject.fileName.stem, select=True)

        self.logger.debug(f'{projectPanel.currentUmlFrameId=}')

    def handleUnsavedProjects(self):

        projectCount: int = self.GetPageCount()
        for idx in range(projectCount):
            projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetPage(idx))
            if projectPanel.umlProjectModified is True:
                self._closeProject(projectPanel=projectPanel)

    # noinspection PyUnusedLocal
    def _onNewProjectDisplayed(self, event: BookCtrlEvent):
        """
        This fires when we add new projects.  Thus, we wind up sending the ACTIVE_DOCUMENT_CHANGED

        Args:
            event:
        """
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        frameId:      FrameId         = projectPanel.currentUmlFrameId

        self.logger.debug(f'{frameId=}')

        self._appPubSubEngine.sendMessage(messageType=MessageType.ACTIVE_DOCUMENT_CHANGED,
                                          uniqueId=EDIT_MENU_HANDLER_ID,
                                          activeFrameId=frameId
                                          )

    # noinspection PyUnusedLocal
    def _frameModifiedListener(self, modifiedFrameId: FrameId):
        """
        Will only be issued when developer modifies current project

        Args:
            modifiedFrameId:
        """
        self._indicateCurrentProjectModified()

    def _currentProjectSavedListener(self, projectPath: Path):
        """
        Will only be issued when the developer is on the current project

        Args:
            projectPath:

        """
        idx:              int = self.GetSelection()
        projectTitle:     str = self._currentProjectTitle
        modifiedTitleStr: str = projectTitle.strip(MODIFIED_INDICATOR)

        assert projectPath.stem == modifiedTitleStr, 'I guess my assumption was wrong'

        self.logger.debug(f'{modifiedTitleStr}')
        self.SetPageText(idx, modifiedTitleStr)

        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        projectPanel.umlProjectModified = False

    def _projectRenamedListener(self, oldName: str, newName: str):
        """
        Will only be issued when developer modifies current project

        Args:
            oldName:  Old project name (bare file name)
            newName:  New project name (bare file name)
        """
        idx:          int = self.GetSelection()
        projectTitle: str = self.GetPageText(idx).strip(MODIFIED_INDICATOR)  # just in case
        assert projectTitle == oldName, 'I guess my assumption was wrong'
        self._renameCurrentProject(newName=newName)

    def _createNewDiagramListener(self, documentType: UmlDocumentType):

        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        frameId: FrameId = projectPanel.createNewDocument(documentType=documentType)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.FRAME_MODIFIED, frameId=frameId, listener=self._frameModifiedListener)
        self._indicateCurrentProjectModified()

    def _documentNameChangedListener(self, projectName: str):
        currentProjectName: str = self.currentProject.umlProject.fileName.stem
        assert currentProjectName == projectName, 'My assumption is wrong'
        self._indicateCurrentProjectModified()

    def _closeProjectListener(self):
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())

        self._closeProject(projectPanel)

    def _getOpenProjectListener(self, callback: OpenProjectsCallback):
        """

        Args:
            callback:   Who to call with the payload
        """

        fileNames: PathList = PathList([])

        projectCount: int = self.GetPageCount()
        for idx in range(projectCount):
            projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetPage(idx))
            fileNames.append(projectPanel.umlProject.fileName)

        callback(fileNames)

    @property
    def _currentProjectPanel(self) -> UmlProjectPanel:
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())

        return projectPanel

    @property
    def _currentProjectTitle(self) -> str:

        idx:          int = self.GetSelection()
        projectTitle: str = self.GetPageText(idx)
        return projectTitle

    def _renameCurrentProject(self, newName: str):

        idx: int = self.GetSelection()
        self.SetPageText(idx, newName)

    def _indicateCurrentProjectModified(self):

        # if self._currentProjectPanel.umlProjectModified is False:
        idx:              int = self.GetSelection()
        projectTitle:     str = self.GetPageText(idx)
        if projectTitle.endswith(MODIFIED_INDICATOR):
            pass
        else:
            modifiedTitleStr: str = f'{projectTitle}{MODIFIED_INDICATOR}'

            # pageIndex: int = self.GetSelection()
            self.SetPageText(idx, modifiedTitleStr)

            projectPanel: UmlProjectPanel = self._currentProjectPanel
            projectPanel.umlProjectModified = True

    def _closeProject(self, projectPanel: UmlProjectPanel):

        if projectPanel.umlProjectModified is True:

            message: str = f'Project: {projectPanel.umlProject.fileName.stem} is modified.  Save it before closing?'
            askDialog: MessageDialog = MessageDialog(parent=None, message=message, caption='Please confirm', style=YES_NO | ICON_QUESTION)
            ans: int = askDialog.ShowModal()
            if ans == ID_YES:
                umlProjectIO: UmlProjectIO = UmlProjectIO(appPubSubEngine=self._appPubSubEngine)
                umlProjectIO.saveProject(umlProject=self.currentProject.umlProject)

        projectName: str = str(self.currentProject.umlProject.fileName)
        pageIdx:     int = self.GetSelection()
        self.DeletePage(pageIdx)
        self.logger.info(f'Project closed: {projectName}')

    def _deleteDiagramListener(self):
        """
        Deletes the currently visible diagram

        """
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        diagramName: str = projectPanel.deleteCurrentDiagram()
        self._indicateCurrentProjectModified()
        self.logger.info(f'Diagram {diagramName} removed from project {projectPanel.umlProject.fileName}')

    def _requestFrameInformationListener(self, callback: Callable):

        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
        from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame
        from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

        projectPanel: UmlProjectPanel = self._currentProjectPanel
        currentFrame: UmlFrame        = projectPanel.currentFrame

        size: Size = self.GetSize()
        #
        # Fix this in umlextensions
        #
        if isinstance(currentFrame, ClassDiagramFrame):
            documentType: str = UmlDocumentType.CLASS_DOCUMENT.value
        elif isinstance(currentFrame, UseCaseDiagramFrame):
            documentType = UmlDocumentType.USE_CASE_DOCUMENT.value
        elif isinstance(currentFrame, SequenceDiagramFrame):
            documentType = UmlDocumentType.SEQUENCE_DOCUMENT.value
        else:
            assert False, 'Unknown document type'

        frameInfo: FrameInformation = FrameInformation(
            umlFrame=currentFrame,
            frameActive=True,
            selectedUmlShapes=currentFrame.selectedShapes,
            diagramTitle=projectPanel.currentDiagramName,
            diagramType=documentType,
            frameSize=FrameSize(width=size.width, height=size.height)
        )
        callback(frameInfo)

    def _addShapeListener(self, umlShape: UmlShapeGenre | UmlLinkGenre):
        from umlshapes.frames.UmlFrame import UmlFrame

        projectPanel: UmlProjectPanel = self._currentProjectPanel
        currentFrame: UmlFrame        = projectPanel.currentFrame

        currentFrame.umlDiagram.AddShape(umlShape)
        umlShape.Show(True)

    def _extensionModifiedProjectListener(self):
        self._indicateCurrentProjectModified()

    def _refreshFrameListener(self):
        from umlshapes.frames.UmlFrame import UmlFrame

        projectPanel: UmlProjectPanel = self._currentProjectPanel
        currentFrame: UmlFrame        = projectPanel.currentFrame

        currentFrame.refresh()

    def _wiggleShapesListener(self):
        """
        This is a hack work around to simulate moving the shapes so
        that the links are visible.
        I tried refresh, redraw, and .DrawLinks;  None of it worked


        So much of a hack that it depends on the umlshapes diagram option
        .snapToGrid to be True
        """
        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.ShapeTypes import UmlShapes
        from umlshapes.types.UmlPosition import UmlPosition
        from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

        projectPanel: UmlProjectPanel = self._currentProjectPanel
        currentFrame: UmlFrame        = projectPanel.currentFrame

        umlShapes: UmlShapes = currentFrame.umlShapes

        for shape in umlShapes:

            if isinstance(shape, UmlShapeGenre) is True:

                umlShape: UmlShapeGenre = cast(UmlShapeGenre, shape)

                oldPosition: UmlPosition = umlShape.position
                newPosition: UmlPosition = UmlPosition(x=oldPosition.x + 10, y=oldPosition.y + 10)

                eventHandler: UmlBaseEventHandler = umlShape.GetEventHandler()

                eventHandler.OnDragLeft(draw=True, x=newPosition.x, y=newPosition.y)
                eventHandler.OnDragLeft(draw=True, x=oldPosition.x, y=oldPosition.y)

    def _subscribeToApplicationMessages(self):
        """
        The application wants some services
        """
        self._appPubSubEngine.subscribe(messageType=MessageType.CURRENT_PROJECT_SAVED,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._currentProjectSavedListener
                                        )
        self._appPubSubEngine.subscribe(messageType=MessageType.PROJECT_RENAMED,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._projectRenamedListener
                                        )
        self._appPubSubEngine.subscribe(messageType=MessageType.CREATE_NEW_DIAGRAM,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._createNewDiagramListener
                                        )
        self._appPubSubEngine.subscribe(messageType=MessageType.DOCUMENT_NAME_CHANGED,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._documentNameChangedListener
                                        )
        self._appPubSubEngine.subscribe(messageType=MessageType.CLOSE_PROJECT,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._closeProjectListener
                                        )

        self._appPubSubEngine.subscribe(messageType=MessageType.DELETE_DIAGRAM,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._deleteDiagramListener
                                        )

        self._appPubSubEngine.subscribe(messageType=MessageType.GET_OPEN_PROJECTS,
                                        uniqueId=NOTEBOOK_ID,
                                        listener=self._getOpenProjectListener)

    def _subscribeToExtensionsMessages(self):
        """
        The diagrammer extensions wants some services
        """
        self._extensionsPubSub.subscribe(messageType=ExtensionsMessageType.REQUEST_FRAME_INFORMATION,  listener=self._requestFrameInformationListener)
        self._extensionsPubSub.subscribe(messageType=ExtensionsMessageType.ADD_SHAPE,                  listener=self._addShapeListener)
        self._extensionsPubSub.subscribe(messageType=ExtensionsMessageType.EXTENSION_MODIFIED_PROJECT, listener=self._extensionModifiedProjectListener)
        self._extensionsPubSub.subscribe(messageType=ExtensionsMessageType.REFRESH_FRAME,              listener=self._refreshFrameListener)
        self._extensionsPubSub.subscribe(messageType=ExtensionsMessageType.WIGGLE_SHAPES,              listener=self._wiggleShapesListener)

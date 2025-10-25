
from typing import cast

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

from wx import CallLater

from wx.lib.sized_controls import SizedPanel

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlio.IOTypes import UmlDocumentType

from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID
from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID
from umldiagrammer.UmlProjectIO import UmlProjectIO

from umldiagrammer.UmlProjectPanel import UmlProjectPanel
from umldiagrammer.data.ProjectDossier import ProjectDossier

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

MODIFIED_INDICATOR: str = '*'

class UmlNotebook(Notebook):
    """
    Our own version of a notebook.  Essentially, we need to keep track when the notebook page selection
    changes.  This includes when we add new project tabs

    Project Names are just the project file name with the suffix (aka, just the stem)

    """
    def __init__(self, sizedPanel: SizedPanel, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        self.logger:           Logger           = getLogger(__name__)
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        super().__init__(sizedPanel, style=NB_LEFT)  # TODO: should be an application preference

        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self.Bind(EVT_NOTEBOOK_PAGE_CHANGED, self._onNewProjectDisplayed)

        CallLater(millis=100, callableObj=self.PostSizeEventToParent)
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
                                        listener=self._closeProjectListener)

    @property
    def currentProject(self) -> ProjectDossier:

        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())

        return ProjectDossier(
            umlProject=projectPanel.umlProject,
            modified=projectPanel.umlProjectModified
        )

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

        self.logger.info(f'{projectPanel.currentUmlFrameId=}')

    # noinspection PyUnusedLocal
    def _onNewProjectDisplayed(self, event: BookCtrlEvent):
        """
        This fires when we add new projects.  Thus, we wind up sending the ACTIVE_DOCUMENT_CHANGED

        Args:
            event:
        """
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        frameId:      FrameId         = projectPanel.currentUmlFrameId

        self.logger.info(f'{frameId=}')

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
        self._indicatedCurrentProjectModified()

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

        self.logger.info(f'{modifiedTitleStr}')
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
        projectPanel.createNewDocument(documentType=documentType)

    def _documentNameChangedListener(self, projectName: str):
        currentProjectName: str = self.currentProject.umlProject.fileName.stem
        assert currentProjectName == projectName, 'My assumption is wrong'
        self._indicatedCurrentProjectModified()

    def _closeProjectListener(self):
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        if projectPanel.umlProjectModified is True:

            message: str = f'Project: {projectPanel.umlProject.fileName.stem} is modified.  Save it before closing?'
            askDialog: MessageDialog = MessageDialog(parent=None, message=message, caption='Please confirm', style=YES_NO | ICON_QUESTION)
            ans: int = askDialog.ShowModal()
            if ans == ID_YES:
                umlProjectIO: UmlProjectIO = UmlProjectIO(appPubSubEngine=self._appPubSubEngine)
                umlProjectIO.saveProject(umlProject=self.currentProject.umlProject)

        pageIdx: int = self.GetSelection()
        self.DeletePage(pageIdx)

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

    def _indicatedCurrentProjectModified(self):

        if self._currentProjectPanel.umlProjectModified is False:
            idx:              int = self.GetSelection()
            projectTitle:     str = self.GetPageText(idx)
            modifiedTitleStr: str = f'{projectTitle}{MODIFIED_INDICATOR}'

            pageIndex: int = self.GetSelection()
            self.SetPageText(pageIndex, modifiedTitleStr)

            projectPanel: UmlProjectPanel = self._currentProjectPanel
            projectPanel.umlProjectModified = True

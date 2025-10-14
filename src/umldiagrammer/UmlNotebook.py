
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import NB_LEFT
from wx import EVT_NOTEBOOK_PAGE_CHANGED

from wx import Notebook
from wx import BookCtrlEvent

from wx import CallLater

from wx.lib.sized_controls import SizedPanel

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID
from umldiagrammer.DiagrammerTypes import ProjectInformation
from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID

from umldiagrammer.UmlProjectPanel import UmlProjectPanel

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

    @property
    def currentProject(self) -> ProjectInformation:

        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())

        return ProjectInformation(
            umlProject=projectPanel.umlProject,
            modified=projectPanel.umlProjectModified
        )

    def addProject(self, projectPanel: UmlProjectPanel):
        """
        Use this method to add a notebook page;  Do not use .AddPage directly

        Args:
            projectPanel:
        """
        for frameId in projectPanel.frameIdMap.keys():
            self._umlPubSubEngine.subscribe(messageType=UmlMessageType.FRAME_MODIFIED, frameId=frameId, listener=self._frameModifiedListener)

        self.AddPage(page=projectPanel, text=projectPanel.umlProject.fileName.stem, select=True)

        self.logger.info(f'{projectPanel.currentUmlFrameId=}')
        self._appPubSubEngine.sendMessage(messageType=MessageType.ACTIVE_DOCUMENT_CHANGED,
                                          uniqueId=EDIT_MENU_HANDLER_ID,
                                          activeFrameId=projectPanel.currentUmlFrameId
                                          )

    # noinspection PyUnusedLocal
    def _onNewProjectDisplayed(self, event: BookCtrlEvent):
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
        if self._currentProjectPanel.umlProjectModified is False:
            idx:              int = self.GetSelection()
            projectTitle:     str = self.GetPageText(idx)
            modifiedTitleStr: str = f'{projectTitle}{MODIFIED_INDICATOR}'

            pageIndex: int = self.GetSelection()
            self.SetPageText(pageIndex, modifiedTitleStr)

            projectPanel: UmlProjectPanel = self._currentProjectPanel
            projectPanel.umlProjectModified = True

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
        projectTitle: str = self.GetPageText(idx)
        assert projectTitle == oldName, 'I guess my assumption was wrong'
        self._renameCurrentProject(newName=newName)

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

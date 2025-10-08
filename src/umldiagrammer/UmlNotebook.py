
from typing import cast

from logging import Logger
from logging import getLogger

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

    def _frameModifiedListener(self, modifiedFrameId: FrameId):

        # Will only be issued when developer on current project
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())

        titleStr:         str = projectPanel.frameIdToTitleMap[modifiedFrameId]
        modifiedTitleStr: str = f'{titleStr} {MODIFIED_INDICATOR}'
        pagIndex: int = self.GetSelection()

        self.SetPageText(pagIndex, modifiedTitleStr)
        projectPanel.umlProjectModified = True

    def _currentProjectSavedListener(self, projectName):
        pass

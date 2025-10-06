
from logging import Logger
from logging import getLogger
from typing import cast

from wx import NB_LEFT
from wx import EVT_NOTEBOOK_PAGE_CHANGED

from wx import Notebook
from wx import BookCtrlEvent

from wx import CallLater

from wx.lib.sized_controls import SizedPanel

from umlio.IOTypes import UmlProject

from umlshapes.frames.DiagramFrame import FrameId

from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID

from umldiagrammer.UmlProjectPanel import UmlProjectPanel

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


class UmlNotebook(Notebook):
    """
    Our own version of a notebook.  Essentially, we need to keep track when the notebook page selection
    changes.  This includes when we add new project tabs
    """
    def __init__(self, sizedPanel: SizedPanel, appPubSubEngine: IAppPubSubEngine):

        self.logger:           Logger           = getLogger(__name__)
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        super().__init__(sizedPanel, style=NB_LEFT)  # TODO: should be an application preference

        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self.Bind(EVT_NOTEBOOK_PAGE_CHANGED, self._onNewProjectDisplayed)
        CallLater(millis=100, callableObj=self.PostSizeEventToParent)

    @property
    def currentProject(self) -> UmlProject:
        projectPanel: UmlProjectPanel = cast(UmlProjectPanel, self.GetCurrentPage())
        return projectPanel.umlProject

    def addProject(self, projectPanel: UmlProjectPanel):
        """
        Use this method to add a notebook page;  Do not use .AddPage directly

        Args:
            projectPanel:
        """
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

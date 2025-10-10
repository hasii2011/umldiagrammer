
from logging import Logger
from logging import getLogger

from wx import Size
from wx import Window
from wx import SplitterWindow

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlio.IOTypes import UmlProject

from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID
from umldiagrammer.DiagrammerTypes import FrameIdMap
from umldiagrammer.DiagrammerTypes import FrameIdToTitleMap

from umldiagrammer.UmlDocumentManager import UmlDocumentManager
from umldiagrammer.UmlProjectTree import TreeNodeData
from umldiagrammer.UmlProjectTree import UmlProjectTree

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueIds
from umldiagrammer.pubsubengine.MessageType import MessageType


class UmlProjectPanel(SplitterWindow):
    def __init__(self, parent: Window, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine, umlProject: UmlProject):
        """

        Args:
            parent:
            appPubSubEngine:    The event engine that the applications uses to communicate within its UI components
            umlPubSubEngine:    The pub sub engine that UML Shapes uses to communicate within itself and the wrapper application
            umlProject:
        """

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent)

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        self._projectTree:     UmlProjectTree     = UmlProjectTree(parent=self, appPubSubEngine=appPubSubEngine, umlProject=umlProject)
        self._documentManager: UmlDocumentManager = UmlDocumentManager(parent=self, umlPubSubEngine=umlPubSubEngine, umlDocuments=umlProject.umlDocuments)

        self.SetMinimumPaneSize(200)            # TODO: This should be a preference

        self.SplitVertically(self._projectTree, self._documentManager)

        uniqueNodeIds: UniqueIds = self._projectTree.uniqueNodeIds
        for uniqueId in uniqueNodeIds:
            self._appPubSubEngine.subscribe(messageType=MessageType.DOCUMENT_SELECTION_CHANGED,
                                            uniqueId=uniqueId,
                                            listener=self._diagramSelectionChangedListener)

        windowSize: Size = parent.GetSize()

        sashPosition: int = round(windowSize.width * 0.3)     # TODO:  This should be a preference
        self.logger.info(f'{sashPosition=}')
        self.SetSashPosition(position=sashPosition, redraw=True)

        self._umlProject:         UmlProject = umlProject
        self._umlProjectModified: bool       = False

    @property
    def umlProject(self) -> UmlProject:
        self._umlProject.umlDocuments = self._documentManager.umlDocuments
        return self._umlProject

    @property
    def umlProjectModified(self) -> bool:
        return self._umlProjectModified

    @umlProjectModified.setter
    def umlProjectModified(self, modified: bool):
        self._umlProjectModified = modified

    @property
    def frameIdMap(self) -> FrameIdMap:
        return self._documentManager.frameIdMap

    @property
    def frameIdToTitleMap(self) -> FrameIdToTitleMap:
        return self._documentManager.frameIdToTitleMap

    @property
    def currentUmlFrameId(self) -> FrameId:
        return self._documentManager.currentUmlFrameId

    def _diagramSelectionChangedListener(self, treeData: TreeNodeData):
        self.logger.debug(f'{treeData=}')
        self._documentManager.switchToDocument(treeData.umlDocument)
        self._appPubSubEngine.sendMessage(messageType=MessageType.ACTIVE_DOCUMENT_CHANGED,
                                          uniqueId=EDIT_MENU_HANDLER_ID,
                                          activeFrameId=self.currentUmlFrameId
                                          )

    def __str__(self) -> str:
        return self._umlProject.fileName.stem

    def __repr__(self) -> str:
        return self.__str__()

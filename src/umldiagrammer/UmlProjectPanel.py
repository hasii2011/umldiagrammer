

from logging import Logger
from logging import getLogger

from wx import Size
from wx import Window
from wx import SplitterWindow

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlio.IOTypes import UmlProject

from umldiagrammer.UmlDocumentManager import UmlDocumentManager
from umldiagrammer.UmlProjectTree import TreeData
from umldiagrammer.UmlProjectTree import TreeNodeIDs
from umldiagrammer.UmlProjectTree import UmlProjectTree

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId
from umldiagrammer.pubsubengine.MessageType import MessageType


class UmlProjectPanel(SplitterWindow):
    def __init__(self, parent: Window, appPubSubEngine: IAppPubSubEngine, umlPubSibEngine: UmlPubSubEngine, umlProject: UmlProject):
        """

        Args:
            parent:
            appPubSubEngine:    The event engine that the applications uses to communicate within its UI components
            umlPubSibEngine:    The pub sub engine that UML Shapes uses to communicate within itself and the wrapper application
            umlProject:
        """

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent)

        self.appEventEngine: IAppPubSubEngine = appPubSubEngine

        self._projectTree:    UmlProjectTree     = UmlProjectTree(parent=self, appPubSubEngine=appPubSubEngine, umlProject=umlProject)
        self._diagramManager: UmlDocumentManager = UmlDocumentManager(parent=self, umlPubSubEngine=umlPubSibEngine, umlDocuments=umlProject.umlDocuments)

        self.SetMinimumPaneSize(200)

        self.SplitVertically(self._projectTree, self._diagramManager)

        treeNodeIDs: TreeNodeIDs = self._projectTree.treeNodeIDs
        for treeNodeID in treeNodeIDs:
            self.appEventEngine.subscribe(eventType=MessageType.DIAGRAM_SELECTION_CHANGED,
                                          uniqueId=UniqueId(treeNodeID),
                                          callback=self._onDiagramSelectionChanged)

        windowSize: Size = parent.GetSize()

        sashPosition: int = round(windowSize.width * 0.3)     # TODO:  This should be a preference
        self.logger.info(f'{sashPosition=}')
        self.SetSashPosition(position=sashPosition, redraw=True)

    def _onDiagramSelectionChanged(self, treeData: TreeData):
        self.logger.debug(f'{treeData=}')
        self._diagramManager.setPage(treeData.documentName)

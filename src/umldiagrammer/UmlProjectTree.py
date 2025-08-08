
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import EVT_TREE_SEL_CHANGED
from wx import TR_HAS_BUTTONS
from wx import TR_HIDE_ROOT

from wx import TreeCtrl
from wx import TreeEvent
from wx import TreeItemId
from wx import Window

from umlshapes.UmlUtils import UmlUtils

from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlProject

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId
from umldiagrammer.pubsubengine.MessageType import MessageType

TreeNodeID = NewType('TreeNodeID', str)


@dataclass
class TreeData:
    documentName: UmlDocumentTitle
    treeNodeID:   TreeNodeID        # The underlying TreeItemId (ID) is opaque


TreeNodeIDs = NewType('TreeNodeIDs', List[TreeNodeID])


class UmlProjectTree(TreeCtrl):
    def __init__(self, parent: Window, umlProject: UmlProject, appPubSubEngine: IAppPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, style=TR_HAS_BUTTONS | TR_HIDE_ROOT)

        self._umlProject:      UmlProject       = umlProject
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._treeNodeIDs:     TreeNodeIDs      = TreeNodeIDs([])

        self.root: TreeItemId = self.AddRoot(umlProject.fileName.stem)

        self._createDocumentNodes()

        self.SelectItem(self.GetFirstChild(self.root)[0])

        self.Bind(EVT_TREE_SEL_CHANGED, self._onDiagramSelectionChanged)

    @property
    def treeNodeIDs(self) -> TreeNodeIDs:
        return self._treeNodeIDs

    def _createDocumentNodes(self):

        for documentName in self._umlProject.umlDocuments.keys():
            documentNode: TreeItemId = self.AppendItem(self.root, documentName)

            treeNodeID: TreeNodeID = TreeNodeID(UmlUtils.getID())
            treeData:   TreeData   = TreeData(
                documentName=documentName,
                treeNodeID=treeNodeID
            )
            self._treeNodeIDs.append(treeNodeID)

            self.SetItemData(item=documentNode, data=treeData)

    def _onDiagramSelectionChanged(self, treeEvent: TreeEvent):

        selectedItem: TreeItemId = treeEvent.GetItem()

        if selectedItem != self.root:
            treeData: TreeData = self.GetItemData(selectedItem)

            self.logger.info(f'{treeData=}')

            self._appPubSubEngine.sendMessage(MessageType.DIAGRAM_SELECTION_CHANGED,
                                              uniqueId=UniqueId(treeData.treeNodeID),
                                              treeData=treeData)

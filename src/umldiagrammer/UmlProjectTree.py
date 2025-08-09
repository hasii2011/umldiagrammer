
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import CANCEL
from wx import CENTRE
from wx import EVT_MENU
from wx import EVT_MENU_CLOSE
from wx import EVT_TREE_SEL_CHANGED
from wx import ID_OK
from wx import ITEM_NORMAL
from wx import MenuEvent
from wx import OK
from wx import TR_HAS_BUTTONS
from wx import TR_HIDE_ROOT
from wx import EVT_TREE_ITEM_RIGHT_CLICK

from wx import TreeCtrl
from wx import TreeEvent
from wx import TreeItemId
from wx import Window
from wx import Menu
from wx import CommandEvent
from wx import TextEntryDialog

from wx import NewIdRef as wxNewIdRef

from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlProject
from umlio.IOTypes import UmlDocument

from umlshapes.UmlUtils import UmlUtils

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId
from umldiagrammer.pubsubengine.MessageType import MessageType


# Used as topic IDs
TreeNodeTopicId  = NewType('TreeNodeTopicId', str)

@dataclass
class TreeNodeData:
    umlDocument:     UmlDocument
    treeNodeID:      TreeItemId        # The underlying TreeItemId (ID) is opaque
    treeNodeTopicId: TreeNodeTopicId


TreeNodeTopicIds = NewType('TreeNodeTopicIds', List[TreeNodeTopicId])

NO_TREE_NODE_DATA: TreeNodeData = cast(TreeNodeData, None)


class UmlProjectTree(TreeCtrl):
    def __init__(self, parent: Window, umlProject: UmlProject, appPubSubEngine: IAppPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, style=TR_HAS_BUTTONS | TR_HIDE_ROOT)

        self._umlProject:       UmlProject       = umlProject
        self._appPubSubEngine:  IAppPubSubEngine = appPubSubEngine
        self._treeNodeTopicIDs: TreeNodeTopicIds = TreeNodeTopicIds([])

        self.root: TreeItemId = self.AddRoot(umlProject.fileName.stem)

        self._createDocumentNodes()

        self.SelectItem(self.GetFirstChild(self.root)[0])

        self.Bind(EVT_TREE_SEL_CHANGED, self._onDocumentSelectionChanged)
        self.Bind(EVT_TREE_ITEM_RIGHT_CLICK, self._onProjectTreeRightClick)

        self._documentPopupMenu:        Menu         = cast(Menu, None)
        self._rightClickedTreeNodeData: TreeNodeData = NO_TREE_NODE_DATA

    @property
    def treeNodeTopicIds(self) -> TreeNodeTopicIds:
        """
        These are used to send out messages for changes to tree nodes

        Returns:  The list of topic IDs

        """
        return self._treeNodeTopicIDs

    def _onProjectTreeRightClick(self, treeEvent: TreeEvent):

        itemId:       TreeItemId = treeEvent.GetItem()
        treeNodeData: TreeNodeData = self.GetItemData(item=itemId)

        self.logger.debug(f'{treeNodeData=}')

        self._rightClickedTreeNodeData = treeNodeData
        self._popupProjectDiagramMenu()

    def _createDocumentNodes(self):

        for documentName, umlDocument in self._umlProject.umlDocuments.items():
            documentNode:    TreeItemId      = self.AppendItem(self.root, documentName)
            treeNodeTopicId: TreeNodeTopicId = TreeNodeTopicId(UmlUtils.getID())

            treeData: TreeNodeData = TreeNodeData(
                umlDocument=umlDocument,
                treeNodeID=documentNode,
                treeNodeTopicId=treeNodeTopicId
            )

            self._treeNodeTopicIDs.append(treeNodeTopicId)
            self.SetItemData(item=documentNode, data=treeData)

    def _onDocumentSelectionChanged(self, treeEvent: TreeEvent):

        selectedItem: TreeItemId = treeEvent.GetItem()

        if selectedItem != self.root:
            treeData: TreeNodeData = self.GetItemData(selectedItem)

            self.logger.info(f'{treeData=}')

            self._appPubSubEngine.sendMessage(MessageType.DOCUMENT_SELECTION_CHANGED,
                                              uniqueId=UniqueId(treeData.treeNodeTopicId),
                                              treeData=treeData)

    def _popupProjectDiagramMenu(self):
        """
        """
        self._appPubSubEngine.sendMessage(eventType=MessageType.UPDATE_APPLICATION_STATUS, uniqueId=APPLICATION_FRAME_ID, message='Select document action')

        if self._documentPopupMenu is None:

            self.logger.debug(f'Create the diagram popup menu')

            [editDiagramNameMenuID, deleteDiagramMenuID] = wxNewIdRef(2)

            popupMenu: Menu = Menu('Actions')
            popupMenu.AppendSeparator()
            popupMenu.Append(editDiagramNameMenuID, 'Edit Diagram Name', 'Change diagram name', ITEM_NORMAL)
            popupMenu.Append(deleteDiagramMenuID,   'Delete Diagram',    'Delete it',           ITEM_NORMAL)

            popupMenu.Bind(EVT_MENU, self._onEditDiagramName, id=editDiagramNameMenuID)
            # popupMenu.Bind(EVT_MENU, self._onDeleteDiagram, id=deleteDiagramMenuID)
            #
            popupMenu.Bind(EVT_MENU_CLOSE, self._onPopupMenuClose)

            self._documentPopupMenu = popupMenu

        # self.logger.debug(f'Current diagram: `{self._projectManager.currentDocument}`')
        self.GetParent().PopupMenu(self._documentPopupMenu)

    # noinspection PyUnusedLocal
    def _onEditDiagramName(self, event: CommandEvent):

        assert self._rightClickedTreeNodeData is not None, 'Developer error'

        rightClickedTreeNodeData: TreeNodeData     = self._rightClickedTreeNodeData
        oldDocumentTitle:         UmlDocumentTitle = rightClickedTreeNodeData.umlDocument.documentTitle

        parent: Window = self.GetParent()
        with TextEntryDialog(parent, "Edit Diagram Title", "Diagram Title", oldDocumentTitle, OK | CANCEL | CENTRE) as dlg:
            if dlg.ShowModal() == ID_OK:
                newDocumentTitle: UmlDocumentTitle = UmlDocumentTitle(dlg.GetValue())
                # self.umlPubSibEngine.sendMessage(eventType=MessageType.DOCUMENT_MODIFIED)
                self.logger.info(f'Diagram named changed from `{oldDocumentTitle}` to `{newDocumentTitle.title}`')

                # Change the model and then the UI
                rightClickedTreeNodeData.umlDocument.documentTitle = newDocumentTitle
                self.SetItemText(self._rightClickedTreeNodeData.treeNodeID, newDocumentTitle)

        self._rightClickedTreeNodeData = NO_TREE_NODE_DATA

    # noinspection PyUnusedLocal
    def _onPopupMenuClose(self, event: MenuEvent):
        """
        I want to clean up my messages
        Args:
            event:
        """
        self._appPubSubEngine.sendMessage(eventType=MessageType.UPDATE_APPLICATION_STATUS, uniqueId=APPLICATION_FRAME_ID, message='')

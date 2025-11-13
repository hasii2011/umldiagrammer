
from logging import Logger
from logging import getLogger

from umlio.IOTypes import UmlDocument
from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlDocumentType
from wx import Menu
from wx import Size
from wx import Window
from wx import SplitterWindow

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlio.IOTypes import UmlProject

from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID
from umldiagrammer.DiagrammerTypes import FrameIdMap
from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID

from umldiagrammer.UmlDiagramManager import UmlDiagramManager
from umldiagrammer.UmlProjectTree import TreeNodeData
from umldiagrammer.UmlProjectTree import UmlProjectTree

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueIds
from umldiagrammer.pubsubengine.MessageType import MessageType


class UmlProjectPanel(SplitterWindow):
    """
    Handles the interactions between the tree nodes (document selection) on the left and the
    diagrammer frames on the right
    """
    def __init__(self, parent: Window, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine, umlProject: UmlProject, editMenu: Menu):
        """

        Args:
            parent:
            appPubSubEngine:    The event engine that the applications uses to communicate within its UI components
            umlPubSubEngine:    The pub sub engine that UML Shapes uses to communicate within itself and the wrapper application
            umlProject:
            editMenu:
        """

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent)

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._editMenu:        Menu             = editMenu

        self._projectTree:      UmlProjectTree     = UmlProjectTree(parent=self, appPubSubEngine=appPubSubEngine, umlProject=umlProject)
        self._umlDiagramManager: UmlDiagramManager = UmlDiagramManager(parent=self,
                                                                       appPubSubEngine=appPubSubEngine,
                                                                       umlPubSubEngine=umlPubSubEngine,
                                                                       umlDocuments=umlProject.umlDocuments,
                                                                       editMenu=editMenu
                                                                       )

        self.SetMinimumPaneSize(200)            # TODO: This should be a preference

        self.SplitVertically(self._projectTree, self._umlDiagramManager)

        uniqueNodeIds: UniqueIds = self._projectTree.uniqueNodeIds
        for uniqueId in uniqueNodeIds:
            self._appPubSubEngine.subscribe(messageType=MessageType.DOCUMENT_SELECTION_CHANGED,
                                            uniqueId=uniqueId,
                                            listener=self._diagramSelectionChangedListener)
            self._appPubSubEngine.subscribe(MessageType.DOCUMENT_NAME_CHANGED,
                                            uniqueId=uniqueId,
                                            listener=self._documentNameChangedListener)

            self._appPubSubEngine.subscribe(MessageType.DELETE_DIAGRAM,
                                            uniqueId=uniqueId,
                                            listener=self._deleteDiagramListener)

        windowSize:  Size = parent.GetSize()
        sashPosition: int = round(windowSize.width * 0.3)     # TODO:  This should be a preference
        self.logger.debug(f'{sashPosition=}')
        self.SetSashPosition(position=sashPosition, redraw=True)

        self._umlProject:         UmlProject = umlProject
        self._umlProjectModified: bool       = False

    @property
    def umlProject(self) -> UmlProject:
        self._umlProject.umlDocuments = self._umlDiagramManager.umlDocuments
        return self._umlProject

    @property
    def umlProjectModified(self) -> bool:
        return self._umlProjectModified

    @umlProjectModified.setter
    def umlProjectModified(self, modified: bool):
        self._umlProjectModified = modified
        #
        # Now tell each of the frames
        #
        if modified is False:
            self._umlDiagramManager.markFramesSaved()

    @property
    def frameIdMap(self) -> FrameIdMap:
        return self._umlDiagramManager.frameIdMap

    @property
    def currentUmlFrameId(self) -> FrameId:
        return self._umlDiagramManager.currentUmlFrameId

    def createNewDocument(self, documentType: UmlDocumentType):
        """

        Args:
            documentType:
        """
        if documentType == UmlDocumentType.CLASS_DOCUMENT:
            umlDocument: UmlDocument = UmlDocument.classDocument()
        elif documentType == UmlDocumentType.USE_CASE_DOCUMENT:
            umlDocument = UmlDocument.useCaseDocument()
        elif documentType == UmlDocumentType.SEQUENCE_DOCUMENT:
            umlDocument = UmlDocument.sequenceDocument()
        else:
            assert False, 'Unknown UML document type'
        #
        # the following 2 lines ensure that document names within a project are unique
        #
        uniqueDocumentTitle: UmlDocumentTitle = self._umlDiagramManager.createUniqueDocumentName(umlDocument.documentTitle)

        umlDocument.documentTitle = uniqueDocumentTitle

        treeNodeTopicId: UniqueId = self._projectTree.createTreeItem(umlDocument=umlDocument, selectItem=True)
        self._umlDiagramManager.createNewDiagram(umlDocument=umlDocument)

        self._umlDiagramManager.switchToDocumentDiagram(umlDocument)
        self._appPubSubEngine.sendMessage(messageType=MessageType.ACTIVE_DOCUMENT_CHANGED,
                                          uniqueId=EDIT_MENU_HANDLER_ID,
                                          activeFrameId=self.currentUmlFrameId
                                          )

        self._appPubSubEngine.subscribe(messageType=MessageType.DOCUMENT_SELECTION_CHANGED,
                                        uniqueId=treeNodeTopicId,
                                        listener=self._diagramSelectionChangedListener)

    def _diagramSelectionChangedListener(self, treeData: TreeNodeData):
        self.logger.debug(f'{treeData=}')
        self._umlDiagramManager.switchToDocumentDiagram(treeData.umlDocument)
        self._appPubSubEngine.sendMessage(messageType=MessageType.ACTIVE_DOCUMENT_CHANGED,
                                          uniqueId=EDIT_MENU_HANDLER_ID,
                                          activeFrameId=self.currentUmlFrameId
                                          )

    def _documentNameChangedListener(self, oldDocumentTitle: UmlDocumentTitle, newDocumentTitle: UmlDocumentTitle):

        self.logger.debug(f'{oldDocumentTitle=} {newDocumentTitle=}')
        self._umlDiagramManager.renameDiagram(oldDocumentTitle=oldDocumentTitle, newDocumentTitle=newDocumentTitle)

        self._appPubSubEngine.sendMessage(messageType=MessageType.DOCUMENT_NAME_CHANGED,
                                          uniqueId=NOTEBOOK_ID,
                                          projectName=self._umlProject.fileName.stem)

    def _deleteDiagramListener(self, diagramName: str):
        self._umlDiagramManager.deleteDiagram(documentName=diagramName)

    def __str__(self) -> str:
        return self._umlProject.fileName.stem

    def __repr__(self) -> str:
        return self.__str__()

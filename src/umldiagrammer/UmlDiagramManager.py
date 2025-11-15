
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Menu
from wx import Window
from wx import Simplebook

from pyutmodelv2.PyutInterface import PyutInterfaces

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.types.Common import UmlShapeList
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.frames.DiagramFrame import FrameId
from umlshapes.frames.DiagramFrame import DiagramFrame
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler
from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase
from umlshapes.shapes.UmlControlPoint import UmlControlPoint

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.links.UmlLink import UmlLink
from umlshapes.links.UmlNoteLink import UmlNoteLink
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler
from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLollipopInterfaceEventHandler import UmlLollipopInterfaceEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlio.IOTypes import UmlActors
from umlio.IOTypes import UmlClasses
from umlio.IOTypes import UmlDocument
from umlio.IOTypes import UmlDocumentType
from umlio.IOTypes import UmlDocuments
from umlio.IOTypes import UmlLinks
from umlio.IOTypes import UmlNotes
from umlio.IOTypes import UmlTexts
from umlio.IOTypes import UmlUseCases
from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlLollipopInterfaces

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.DiagrammerTypes import FrameIdMap
from umldiagrammer.DiagrammerTypes import UmlShapeGenre
from umldiagrammer.UniqueNameGenerator import NameList
from umldiagrammer.UniqueNameGenerator import createUniqueName
from umldiagrammer.data.LollipopCreationData import LollipopCreationData

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId
from umldiagrammer.pubsubengine.MessageType import MessageType

# TODO:  This might belong in umlshapes
DiagramFrameType = ClassDiagramFrame | UseCaseDiagramFrame | SequenceDiagramFrame

class UmlDiagramManager(Simplebook):
    def __init__(self, parent: Window, umlDocuments: UmlDocuments, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine, editMenu: Menu):
        """
        Assumes that the provided UML documents all belong to the same project

        Args:
            parent:             Parent window
            umlDocuments:       UmlDocuments the diagram manager will switch between
            appPubSubEngine:    The application pub/sub engine
            umlPubSubEngine:    The Uml pub/sub engine, In case something happens on the diagram frame
            editMenu:
        """

        self.logger:          Logger                = getLogger(__name__)
        self._preferences:    DiagrammerPreferences = DiagrammerPreferences()
        self._umlPreferences: UmlPreferences        = UmlPreferences()

        super().__init__(parent=parent)

        self._umlDocuments:    UmlDocuments     = umlDocuments
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._editMenu:        Menu             = editMenu

        self._frameIdMap: FrameIdMap = FrameIdMap({})

        # doing any effect should be an application preference
        # self.SetEffect(effect=SHOW_EFFECT_SLIDE_TO_RIGHT)               # TODO:  Should be an application preference
        # self.SetEffectTimeout(timeout=200)                              # TODO:  Should be an application preference

        self._createDiagramPages()
        self.SetSelection(0)

    @property
    def umlDocuments(self) -> UmlDocuments:
        """
        The input document at UI creation may be out of date.  So recreate it by
        re-reading the shapes from the frames;  Update the internal variable and
        return it

        Returns:  The updated UML Documents

        """
        umlDocuments: UmlDocuments = UmlDocuments({})
        pageCount: int = self.GetPageCount()

        for pageIdx in range(0, pageCount):

            umlDocument: UmlDocument = UmlDocument()
            page:         Window = self.GetPage(pageIdx)
            currentTitle: str    = self.GetPageText(pageIdx)

            if isinstance(page, ClassDiagramFrame):
                classDiagramFrame: ClassDiagramFrame = page
                umlDocument.documentType = UmlDocumentType.CLASS_DOCUMENT
                umlDocument = self._toBasicUmlDocument(umlDocument=umlDocument, documentTitle=currentTitle, diagramFrame=classDiagramFrame)
            elif isinstance(page, UseCaseDiagramFrame):
                useCaseDiagramFrame: UseCaseDiagramFrame = page
                umlDocument.documentType = UmlDocumentType.USE_CASE_DOCUMENT
                umlDocument = self._toBasicUmlDocument(umlDocument=umlDocument, documentTitle=currentTitle, diagramFrame=useCaseDiagramFrame)
                self.logger.warning('Not yet implemented')
            elif isinstance(page, SequenceDiagramFrame):
                umlDocument.documentType = UmlDocumentType.SEQUENCE_DOCUMENT
                sequenceDiagramFrame: SequenceDiagramFrame = page
                umlDocument = self._toBasicUmlDocument(umlDocument=umlDocument, documentTitle=currentTitle, diagramFrame=sequenceDiagramFrame)
                self.logger.warning('Not yet implemented')
            else:
                assert False, 'No such frame type'

            umlDocument = self._populateUmlDocument(page=page, umlDocument=umlDocument)
            umlDocuments[umlDocument.documentTitle] = umlDocument

        self._umlDocuments = umlDocuments
        return self._umlDocuments

    @property
    def frameIdMap(self) -> FrameIdMap:
        return self._frameIdMap

    @property
    def currentUmlFrame(self) -> UmlFrame:
        return cast(UmlFrame, self.GetCurrentPage())

    @property
    def currentUmlFrameId(self) -> FrameId:

        umlFrame: UmlFrame = cast(UmlFrame, self.GetCurrentPage())

        return umlFrame.id

    def currentDiagramName(self) -> str:
        idx: int = self.GetSelection()
        return self.GetPageText(idx)

    def switchToDocumentDiagram(self, umlDocument: UmlDocument):
        """
        Handles selection within SimpleBook;

        Args:
            umlDocument:
        """
        pageCount:     int = self.GetPageCount()
        documentTitle: str = umlDocument.documentTitle
        for idx in range(pageCount):
            currentTitle: str = self.GetPageText(idx)
            if documentTitle == currentTitle:
                self.SetSelection(idx)
                break

    def renameDiagram(self, oldDocumentTitle: UmlDocumentTitle, newDocumentTitle: UmlDocumentTitle):
        # This is probably not necessary
        changedDocument: UmlDocument = self._umlDocuments[oldDocumentTitle]
        del self._umlDocuments[oldDocumentTitle]
        changedDocument.documentTitle = newDocumentTitle
        self._umlDocuments[newDocumentTitle] = changedDocument

        pageCount:     int = self.GetPageCount()
        for idx in range(pageCount):
            currentTitle: str = self.GetPageText(idx)
            if currentTitle == oldDocumentTitle:
                self.SetPageText(idx, newDocumentTitle)
                break

        self.logger.info(f'Updated: {self._umlDocuments=}')

    def createUniqueDocumentName(self, umlDocumentTitle: UmlDocumentTitle) -> UmlDocumentTitle:
        """
        Ensures that document title within a project are unique

        Args:
            umlDocumentTitle:

        Returns:  Either the original document title unmodified or one that is unique
        within this project
        """
        documentNames: NameList = cast(NameList, self._umlDocuments.keys())
        uniqueName:    str      = createUniqueName(nameToCheck=umlDocumentTitle, names=documentNames)

        return UmlDocumentTitle(uniqueName)

    def createNewDiagram(self, umlDocument: UmlDocument):
        """

        Args:
            umlDocument:
        """

        diagramFrame: DiagramFrameType = self._createDiagramFrame(documentType=umlDocument.documentType)

        self.AddPage(diagramFrame, umlDocument.documentTitle, select=True)
        self._frameIdMap[diagramFrame.id] = diagramFrame
        self._umlDocuments[umlDocument.documentTitle] = umlDocument

    def deleteDiagram(self, diagramName: str):
        """
        No need to update any other internal data structures

        Args:
            diagramName:

        """
        for pageIdx in range(self.GetPageCount()):
            currentName: str = self.GetPageText(pageIdx)
            if currentName == diagramName:
                self.DeletePage(pageIdx)
                self._umlDocuments.pop(UmlDocumentTitle(diagramName))
                break

    def markFramesSaved(self):
        for frameId, frame in self._frameIdMap.items():
            umlFrame: UmlFrame = cast(UmlFrame, frame)
            umlFrame.markFrameSaved()

    def _createLollipopInterfaceListener(self,
                                         requestingFrame:    ClassDiagramFrame,
                                         requestingUmlClass: UmlClass,
                                         pyutInterfaces:     PyutInterfaces,
                                         perimeterPoint:     UmlPosition
                                         ):
        """
        Got the message from the underlying frame.  Pass it on to the application
        so it can put the creation on the command stack

        Args:
            requestingFrame:
            requestingUmlClass:
            pyutInterfaces:
            perimeterPoint:

        """
        lollipopCreationData: LollipopCreationData = LollipopCreationData(requestingFrame=requestingFrame,
                                                                          requestingUmlClass=requestingUmlClass,
                                                                          pyutInterfaces=pyutInterfaces,
                                                                          perimeterPoint=perimeterPoint
                                                                          )

        self._appPubSubEngine.sendMessage(MessageType.LOLLIPOP_CREATION_REQUEST, uniqueId=APPLICATION_FRAME_ID, lollipopCreationData=lollipopCreationData)

    def _updateEditMenuListener(self):
        """
        The 'selected' project has changed;
        """
        umlFrame: UmlFrame = self.currentUmlFrame
        umlFrame.commandProcessor.SetMenuStrings()

    def _createDiagramPages(self):

        for umlDocumentTitle, umlDocument in self._umlDocuments.items():

            documentType: UmlDocumentType  = umlDocument.documentType
            diagramFrame: DiagramFrameType = self._createDiagramFrame(documentType=documentType)

            self.AddPage(diagramFrame, umlDocumentTitle)
            self._frameIdMap[diagramFrame.id] = diagramFrame

            self._layoutShapes(diagramFrame=diagramFrame, umlDocument=umlDocument)

    def _createDiagramFrame(self, documentType: UmlDocumentType) -> DiagramFrameType:
        """

        Args:
            documentType:

        Returns:  A nascent diagram frame of the appropriate type
        """

        if documentType == UmlDocumentType.CLASS_DOCUMENT:
            diagramFrame = ClassDiagramFrame(
                parent=self,
                umlPubSubEngine=self._umlPubSubEngine
            )
            self._umlPubSubEngine.subscribe(UmlMessageType.CREATE_LOLLIPOP, frameId=diagramFrame.id, listener=self._createLollipopInterfaceListener)
        elif documentType == UmlDocumentType.USE_CASE_DOCUMENT:
            diagramFrame = UseCaseDiagramFrame(
                parent=self,
                umlPubSubEngine=self._umlPubSubEngine,
            )
        elif documentType == UmlDocumentType.SEQUENCE_DOCUMENT:
            diagramFrame = SequenceDiagramFrame(
                parent=self,
                umlPubSubEngine=self._umlPubSubEngine
            )
        else:
            assert False, f'Unknown UML document type: {documentType=}'

        diagramFrame.commandProcessor.SetEditMenu(self._editMenu)
        self._appPubSubEngine.subscribe(MessageType.UPDATE_EDIT_MENU, uniqueId=cast(UniqueId, diagramFrame.id), listener=self._updateEditMenuListener)

        umlDiagram: UmlDiagram = diagramFrame.umlDiagram
        if self._umlPreferences.snapToGrid is True:
            umlDiagram.SetSnapToGrid(snap=True)
            umlDiagram.SetGridSpacing(self._umlPreferences.backgroundGridInterval)
        else:
            umlDiagram.SetSnapToGrid(snap=False)

        return diagramFrame

    def _layoutShapes(self, diagramFrame: ClassDiagramFrame | UseCaseDiagramFrame, umlDocument: UmlDocument):

        self._layoutClasses(diagramFrame, umlDocument.umlClasses)
        self._layoutNotes(diagramFrame, umlDocument.umlNotes)
        self._layoutTexts(diagramFrame, umlDocument.umlTexts)
        self._layoutActors(diagramFrame, umlDocument.umlActors)
        self._layoutUseCases(diagramFrame, umlDocument.umlUseCases)
        self._layoutLinks(diagramFrame, umlDocument.umlLinks)
        self._layoutLollipops(diagramFrame, umlDocument.umlLollipopInterfaces)

    def _layoutClasses(self, diagramFrame: ClassDiagramFrame, umlClasses: UmlClasses):
        for umlClass in umlClasses:
            self._layoutShape(
                umlShape=umlClass,
                diagramFrame=diagramFrame,
                eventHandlerClass=UmlClassEventHandler
            )

    def _layoutNotes(self, diagramFrame: ClassDiagramFrame | UseCaseDiagramFrame, umlNotes: UmlNotes):

        for umlNote in umlNotes:
            self._layoutShape(
                umlShape=umlNote,
                diagramFrame=diagramFrame,
                eventHandlerClass=UmlNoteEventHandler
            )

    def _layoutTexts(self, diagramFrame: ClassDiagramFrame, umlTexts: UmlTexts):

        for umlText in umlTexts:
            self._layoutShape(
                umlShape=umlText,
                diagramFrame=diagramFrame,
                eventHandlerClass=UmlTextEventHandler
            )

    def _layoutActors(self, diagramFrame: UseCaseDiagramFrame, umlActors: UmlActors):

        for umlActor in umlActors:
            self._layoutShape(
                umlShape=umlActor,
                diagramFrame=diagramFrame,
                eventHandlerClass=UmlActorEventHandler
            )

    def _layoutUseCases(self, diagramFrame: UseCaseDiagramFrame, umlUseCases: UmlUseCases):
        for umlUseCase in umlUseCases:
            self._layoutShape(
                umlShape=umlUseCase,
                diagramFrame=diagramFrame,
                eventHandlerClass=UmlUseCaseEventHandler
            )

    def _layoutLinks(self, diagramFrame: ClassDiagramFrame | UseCaseDiagramFrame, umlLinks: UmlLinks):
        for umlLink in umlLinks:
            umlLink.umlFrame = diagramFrame
            if isinstance(umlLink, UmlInheritance):
                umInheritance: UmlInheritance = cast(UmlInheritance, umlLink)
                subClass  = umInheritance.subClass
                baseClass = umInheritance.baseClass

                subClass.addLink(umlLink=umInheritance, destinationClass=baseClass)

                diagramFrame.umlDiagram.AddShape(umInheritance)
                umInheritance.Show(True)

                umlLinkEventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlLink)
                umlLinkEventHandler.umlPubSubEngine = self._umlPubSubEngine
                umlLinkEventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlLink.SetEventHandler(umlLinkEventHandler)

            elif isinstance(umlLink, UmlNoteLink):
                umlNoteLink: UmlNoteLink = cast(UmlNoteLink, umlLink)
                sourceNote:       UmlNote  = umlNoteLink.sourceNote
                destinationClass: UmlClass = umlNoteLink.destinationClass

                sourceNote.addLink(umlNoteLink=umlNoteLink, umlClass=destinationClass)

                diagramFrame.umlDiagram.AddShape(umlNoteLink)
                umlNoteLink.Show(True)
                eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink)
                eventHandler.umlPubSubEngine = self._umlPubSubEngine
                eventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlNoteLink.SetEventHandler(eventHandler)
            elif isinstance(umlLink, (UmlAssociation, UmlComposition, UmlAggregation)):

                source      = umlLink.sourceShape
                destination = umlLink.destinationShape
                source.addLink(umlLink, destination)  # type: ignore

                diagramFrame.umlDiagram.AddShape(umlLink)
                umlLink.Show(True)

                umlAssociationEventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlLink)
                umlAssociationEventHandler.umlPubSubEngine = self._umlPubSubEngine
                umlAssociationEventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlLink.SetEventHandler(umlAssociationEventHandler)

    def _layoutLollipops(self, diagramFrame: ClassDiagramFrame, umlLollipops: UmlLollipopInterfaces):

        for umlLollipop in umlLollipops:
            umlLollipopInterface: UmlLollipopInterface = cast(UmlLollipopInterface, umlLollipop)
            umlLollipopInterface.umlFrame = diagramFrame

            self.logger.info(f'{umlLollipopInterface}')

            diagramFrame.umlDiagram.AddShape(umlLollipopInterface)
            umlLollipopInterface.Show(True)
            lollipopEventHandler: UmlLollipopInterfaceEventHandler = UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)
            lollipopEventHandler.umlPubSubEngine = self._umlPubSubEngine
            lollipopEventHandler.SetPreviousHandler(umlLollipopInterface.GetEventHandler())
            umlLollipopInterface.SetEventHandler(lollipopEventHandler)

    def _layoutShape(self, umlShape: UmlShapeGenre, diagramFrame: ClassDiagramFrame | UseCaseDiagramFrame, eventHandlerClass: type[UmlBaseEventHandler]):
        """

        Args:
            umlShape:
            diagramFrame:
            eventHandlerClass:
        """

        umlShape.umlFrame = diagramFrame
        diagram: UmlDiagram = diagramFrame.umlDiagram

        eventHandler: UmlBaseEventHandler = eventHandlerClass()
        eventHandler.SetShape(umlShape)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
        umlShape.SetEventHandler(eventHandler)

        diagram.AddShape(umlShape)
        umlShape.Show(True)

        diagramFrame.refresh()

    def _toBasicUmlDocument(self, umlDocument: UmlDocument, documentTitle: str, diagramFrame: DiagramFrame) -> UmlDocument:
        """
        Document type set by caller
        Args:
            umlDocument:    Partial UML Document
            documentTitle:  The string from the tab (Not visible but maintained)
            diagramFrame:   The associated diagram frame

        Returns:  The updated UML Document (additional meta data)
        """
        scrollPosX, scrollPosY = diagramFrame.GetViewStart()

        xUnit, yUnit = diagramFrame.GetScrollPixelsPerUnit()

        umlDocument.documentTitle   = UmlDocumentTitle(documentTitle)
        umlDocument.scrollPositionX = scrollPosX
        umlDocument.scrollPositionY = scrollPosY
        umlDocument.pixelsPerUnitX  = xUnit
        umlDocument.pixelsPerUnitY  = yUnit

        return umlDocument

    def _populateUmlDocument(self, page: Window, umlDocument: UmlDocument) -> UmlDocument:

        umlFrame: UmlFrame = cast(UmlFrame, page)

        umlShapes: UmlShapeList = umlFrame.umlShapes

        for umlShape in umlShapes:
            # noinspection PyUnusedLocal
            match umlShape:
                case UmlClass() as umlShape:
                    umlDocument.umlClasses.append(umlShape)
                case UmlInheritance() | UmlInterface() | UmlAssociation() as umlShape:
                    umlDocument.umlLinks.append(umlShape)
                case UmlLollipopInterface() as umlShape:
                    umlDocument.umlLinks.append(cast(UmlLink, umlShape))  # temp cast until umlio supports UmlLollipopInterfaces
                case UmlNote() as umlShape:
                    umlDocument.umlNotes.append(umlShape)
                case UmlText() as umlShape:
                    umlDocument.umlTexts.append(umlShape)
                case UmlUseCase() as umlShape:
                    umlDocument.umlUseCases.append(umlShape)
                case UmlActor() as umlShape:
                    umlDocument.umlActors.append(umlShape)
                case UmlControlPoint() as umlShape:
                    pass
                # case OglSDMessage() as umlShape:  # Put here so it does not fall into OglLink
                #     oglSDMessage: OglSDMessage = cast(OglSDMessage, umlShape)
                #     modelId: int = oglSDMessage.pyutObject.id
                #     oglDocument.oglSDMessages[modelId] = oglSDMessage
                #
                # case OglSDInstance() as umlShape:
                #     oglSDInstance: OglSDInstance = cast(OglSDInstance, umlShape)
                #     modelId = oglSDInstance.pyutSDInstance.id
                #     umlDocument.oglSDInstances[modelId] = oglSDInstance
                case _:
                    self.logger.warning(f'Unknown Uml object type: {umlShape}, not saved')

        return umlDocument

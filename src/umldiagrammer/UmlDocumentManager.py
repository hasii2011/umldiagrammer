
from typing import cast

from logging import Logger
from logging import getLogger

from wx import SHOW_EFFECT_SLIDE_TO_RIGHT

from wx import Window
from wx import Simplebook

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.ClassDiagramFrame import CreateLollipopCallback
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler
from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlshapes.links.UmlNoteLink import UmlNoteLink
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlAggregation import UmlAggregation

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler
from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLollipopInterfaceEventHandler import UmlLollipopInterfaceEventHandler

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlio.IOTypes import UmlActors
from umlio.IOTypes import UmlClasses
from umlio.IOTypes import UmlDocument
from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlDocumentType
from umlio.IOTypes import UmlDocuments
from umlio.IOTypes import UmlLinks
from umlio.IOTypes import UmlNotes
from umlio.IOTypes import UmlTexts
from umlio.IOTypes import UmlUseCases

from umldiagrammer.DiagrammerTypes import FrameIdMap
from umldiagrammer.DiagrammerTypes import UmlDocumentTitleToPage

UmlShape = UmlActor | UmlNote | UmlText | UmlUseCase | UmlClass


class UmlDocumentManager(Simplebook):
    def __init__(self, parent: Window, umlDocuments: UmlDocuments, umlPubSubEngine: UmlPubSubEngine):
        """

        Args:
            parent:             Parent window
            umlDocuments:       UmlDocuments the diagram manager will switch between
            umlPubSubEngine:     The Uml Event engine, In case something happens on the diagram frame
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self._umlDocuments:    UmlDocuments    = umlDocuments
        self._umlPubSubEngine: UmlPubSubEngine = umlPubSubEngine

        self._frameIdMap:            FrameIdMap             = FrameIdMap({})
        self._umlDocumentTileToPage: UmlDocumentTitleToPage = UmlDocumentTitleToPage({})

        # doing any effect should be an application preference
        self.SetEffect(effect=SHOW_EFFECT_SLIDE_TO_RIGHT)               # TODO:  Should be an application preference
        self.SetEffectTimeout(timeout=200)                              # TODO:  Should be an application preference

        self._createPages()

        self.SetSelection(0)

    @property
    def frameIdMap(self) -> FrameIdMap:
        return self._frameIdMap

    def setPage(self, umlDocument: UmlDocument):
        self.SetSelection(self._umlDocumentTileToPage[umlDocument.documentTitle])

    def _createPages(self):

        for umlDocumentTitle, umlDocument in self._umlDocuments.items():

            documentType: UmlDocumentType = umlDocument.documentType

            if documentType == UmlDocumentType.CLASS_DOCUMENT:
                diagramFrame = ClassDiagramFrame(
                    parent=self,
                    umlPubSubEngine=self._umlPubSubEngine,
                    createLollipopCallback=cast(CreateLollipopCallback, None)       # TODO:  Where is this
                )
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

            self.AddPage(diagramFrame, umlDocumentTitle)
            self._layoutShapes(diagramFrame=diagramFrame, umlDocument=umlDocument)

            self._frameIdMap[diagramFrame.id] = umlDocument.documentTitle
            self._umlDocumentTileToPage[umlDocumentTitle] = self.GetPageCount() - 1

    def _layoutShapes(self, diagramFrame: ClassDiagramFrame | UseCaseDiagramFrame, umlDocument: UmlDocument):

        self._layoutClasses(diagramFrame, umlDocument.umlClasses)
        self._layoutNotes(diagramFrame, umlDocument.umlNotes)
        self._layoutTexts(diagramFrame, umlDocument.umlTexts)
        self._layoutActors(diagramFrame, umlDocument.umlActors)
        self._layoutUseCases(diagramFrame, umlDocument.umlUseCases)
        self._layoutLinks(diagramFrame, umlDocument.umlLinks)

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

                source = umlLink.sourceShape
                dest   = umlLink.destinationShape
                source.addLink(umlLink, dest)  # type: ignore

                diagramFrame.umlDiagram.AddShape(umlLink)
                umlLink.Show(True)

                umlAssociationEventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlLink)
                umlAssociationEventHandler.umlPubSubEngine = self._umlPubSubEngine
                umlAssociationEventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlLink.SetEventHandler(umlAssociationEventHandler)
            elif isinstance(umlLink, UmlLollipopInterface):
                umlLollipopInterface: UmlLollipopInterface = cast(UmlLollipopInterface, umlLink)
                self.logger.info(f'{umlLollipopInterface}')

                diagramFrame.umlDiagram.AddShape(umlLollipopInterface)
                umlLollipopInterface.Show(True)
                lollipopEventHandler: UmlLollipopInterfaceEventHandler = UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)
                lollipopEventHandler.umlPubSubEngine = self._umlPubSubEngine
                lollipopEventHandler.SetPreviousHandler(umlLollipopInterface.GetEventHandler())
                umlLollipopInterface.SetEventHandler(lollipopEventHandler)

    def _layoutShape(self, umlShape: UmlShape, diagramFrame: ClassDiagramFrame | UseCaseDiagramFrame, eventHandlerClass: type[ShapeEvtHandler]):
        """

        Args:
            umlShape:
            diagramFrame:
            eventHandlerClass:
        """

        umlShape.umlFrame = diagramFrame
        diagram: UmlDiagram = diagramFrame.umlDiagram

        eventHandler: ShapeEvtHandler = eventHandlerClass()
        eventHandler.SetShape(umlShape)
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
        umlShape.SetEventHandler(eventHandler)

        diagram.AddShape(umlShape)
        umlShape.Show(True)

        diagramFrame.refresh()

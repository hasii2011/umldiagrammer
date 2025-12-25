
from typing import Dict
from typing import cast
from typing import Callable

from logging import Logger
from logging import getLogger

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.Note import Note
from umlmodel.enumerations.LinkType import LinkType
from wx import OK
from wx import Point
from wx import ICON_ERROR

from wx import Command
from wx import MessageDialog

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.UmlLink import UmlLink
from umlshapes.links.UmlNoteLink import UmlNoteLink
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance

from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler
from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umldiagrammer.DiagrammerTypes import UmlLinkGenre
from umldiagrammer.DiagrammerTypes import UmlShapeGenre
from umldiagrammer.DiagrammerTypes import UmlAssociationGenre

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine


class BaseWxLinkCommand(Command):

    NO_NAME_MESSAGE: str = "testMessage()"

    def __init__(self,
                 partialName: str,
                 linkType:    LinkType,
                 umlFrame:    UmlFrame,
                 appPubSubEngine: IAppPubSubEngine,
                 umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            partialName: The name of the link;  I call it partial, because it will enhanced here
            linkType:   Type of link
            umlFrame:   The frame it will appear on
            appPubSubEngine:    The application publish/subscribe engine
            umlPubSubEngine:    The UML Shape publish/subscribe engine
        """

        self._name: str = f'{partialName} {self._toCommandName(linkType=linkType)}'

        super().__init__(canUndo=True, name=self._name)

        self._linkLogger:     Logger         = getLogger(__name__)

        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlFrame:        UmlFrame         = umlFrame

        self._sourceUmlShape:      UmlShapeGenre = cast(UmlShapeGenre, None)
        self._destinationUmlShape: UmlShapeGenre = cast(UmlShapeGenre, None)

        self._linkType: LinkType = linkType

        self._srcPoint: Point = cast(Point, None)
        self._dstPoint: Point = cast(Point, None)

        self._link:      UmlLink  = cast(UmlLink, None)
        self._modelLink: Link = cast(Link, None)    # for undo of delete
        self._spline:   bool     = False
        # self._controlPoints: ControlPoints = ControlPoints([])       # for undo of delete or create link from plugin manager

        #
        # Dispatch table, aka dictionary
        #
        self._linkCreationDispatcher: Dict[LinkType, Callable] = {
            LinkType.INHERITANCE: self._createInheritanceLink,
            LinkType.INTERFACE:   self._createInterfaceLink,
            LinkType.NOTELINK:    self._createNoteLink,
            LinkType.ASSOCIATION: self._createAssociationLink,
            LinkType.AGGREGATION: self._createAggregationLink,
            LinkType.COMPOSITION: self._createCompositionLink,
        }

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True

    def _cbDoDeleteLink(self):
        """
        Dual purpose depending on the context
        From CommandCreateUmlLink.Undo or from CommandDeleteUmlLink.Do
        """
        umlFrame: UmlFrame = self._umlFrame

        link: UmlLink = self._link

        if isinstance(link, UmlAssociation):
            umlAssociation: UmlAssociation = cast(UmlAssociation, link)     # noqa
            self._linkLogger.info(f'{umlAssociation} we might have to do something here')
            # if oglAssociation.centerLabel is not None:
            #     oglAssociation.centerLabel.Detach()
            # if oglAssociation.sourceCardinality is not None:
            #     oglAssociation.sourceCardinality.Detach()
            # if oglAssociation.destinationCardinality is not None:
            #     oglAssociation.destinationCardinality.Detach()

        link.Detach()
        self._linkLogger.info(f'{link.__repr__()} deleted')
        umlFrame.Refresh()

    def _cbPlaceLink(self):
        """
        Assumes that self._link was created prior to invoking this method
        Dual purpose depending on context
        From CommandCreateUmlLink.Do and from CommandDeleteOglLink.Undo
        """
        umlFrame: UmlFrame = self._umlFrame

        umlFrame.umlDiagram.AddShape(self._link)
        self._link.Show(True)

        umlFrame.Refresh()

        self._linkLogger.info(f'Created: {self._link}')

    def _createLink(self) -> UmlLinkGenre:
        """

        Returns:  A specific UmlLink instance depending on the link type
        """
        linkType: LinkType = self._linkType
        try:
            return self._linkCreationDispatcher[linkType]()
        except KeyError as ke:
            eMsg: str = f'Maybe it is unimplemented {ke}'
            with MessageDialog(None, eMsg, 'Unknown Link Type', OK | ICON_ERROR) as dlg:
                dlg.ShowModal()

        assert False, 'Unimplemented link type'

    def _createAssociationLink(self) -> UmlAssociation:
        """
        UmlAssociation, UmlAggregation, UmlComposition
        Args:

        Returns:
        """
        sourceClass:      UmlClass = cast(UmlClass, self._sourceUmlShape)               # noqa
        destinationClass: UmlClass = cast(UmlClass, self._destinationUmlShape)          # noqa

        link:           Link                = self._getAppropriateModelLink(source=sourceClass, destination=destinationClass)
        umlAssociation: UmlAssociationGenre = self._getAppropriateAssociation(link=link)

        umlAssociation = self._completeTheAssociationLink(umlAssociation=umlAssociation,
                                                          sourceClass=sourceClass,
                                                          destinationClass=destinationClass,
                                                          link=link
                                                          )

        return umlAssociation

    def _createAggregationLink(self) -> UmlAggregation:

        aggregator: UmlClass = cast(UmlClass, self._sourceUmlShape)             # noqa
        aggregated: UmlClass = cast(UmlClass, self._destinationUmlShape)        # noqa

        link:           Link                = self._getAppropriateModelLink(source=aggregator, destination=aggregated)
        umlAggregation: UmlAssociationGenre = self._getAppropriateAssociation(link=link)

        umlAggregation = self._completeTheAssociationLink(umlAssociation=umlAggregation,
                                                          sourceClass=aggregator,
                                                          destinationClass=aggregated,
                                                          link=link
                                                          )
        return umlAggregation   # type: ignore

    def _createCompositionLink(self) -> UmlComposition:
        composer: UmlClass = cast(UmlClass, self._sourceUmlShape)               # noqa
        composed: UmlClass = cast(UmlClass, self._destinationUmlShape)          # noqa

        link:           Link                = self._getAppropriateModelLink(source=composer, destination=composed)
        umlComposition: UmlAssociationGenre = self._getAppropriateAssociation(link=link)

        umlComposition = self._completeTheAssociationLink(umlAssociation=umlComposition,
                                                          sourceClass=composer,
                                                          destinationClass=composed,
                                                          link=link
                                                          )
        return umlComposition   # type: ignore

    def _completeTheAssociationLink(self, umlAssociation: UmlAssociationGenre, sourceClass: UmlClass, destinationClass: UmlClass, link: Link) -> UmlAssociationGenre:
        """

        Args:
            umlAssociation:
            sourceClass:
            destinationClass:
            link:

        Returns:
        """

        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.umlFrame = self._umlFrame
        umlAssociation.MakeLineControlPoints(n=2)  # Make this configurable

        sourceClass.addLink(umlLink=umlAssociation, destinationClass=destinationClass)
        # add it to the source Model Class
        sourceClass.modelClass.addLink(link)

        # Update the model
        srcModelClass:  Class = sourceClass.modelClass
        destModelClass: Class = destinationClass.modelClass
        destModelClass.addParent(srcModelClass)
        # noinspection PyUnusedLocal
        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation, umlPubSubEngine=self._umlPubSubEngine)

        self._name = self._toCommandName(link.linkType)

        return umlAssociation

    def _createInheritanceLink(self) -> UmlInheritance:
        """
        source == SubClass
        destination == Base Class.  (arrow here)

        Add a parent link between the child and parent objects.

        Returns:
            The inheritance UmlLink
        """
        subClass:  UmlClass = cast(UmlClass, self._sourceUmlShape)                  # noqa
        baseClass: UmlClass = cast(UmlClass, self._destinationUmlShape)             # noqa

        sourceModelClass:      Class = subClass.modelClass
        destinationModelClass: Class = baseClass.modelClass
        # If none, we are creating from scratch
        # If we have a value, we are undoing a delete action
        if self._modelLink is None:
            link: Link  = Link("", linkType=LinkType.INHERITANCE, source=sourceModelClass, destination=destinationModelClass)
        else:
            link = self._modelLink

        umlLink: UmlInheritance = UmlInheritance(link=link, baseClass=baseClass, subClass=subClass)
        umlLink.umlFrame = self._umlFrame
        umlLink.MakeLineControlPoints(n=2)       # Make this configurable

        subClass.addLink(umlLink=umlLink, destinationClass=baseClass)

        # Update the model
        subClassModelClass: Class = subClass.modelClass
        baseModelClass:     Class = baseClass.modelClass

        subClassModelClass.addParent(baseModelClass)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlLink, previousEventHandler=umlLink.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlLink.SetEventHandler(eventHandler)

        return umlLink

    def _createInterfaceLink(self) -> UmlInterface:

        interface:      UmlClass = cast(UmlClass, self._destinationUmlShape)        # noqa
        implementation: UmlClass = cast(UmlClass, self._sourceUmlShape)             # noqa

        implementorModelClass: Class = implementation.modelClass
        interfaceModelClass:   Class = interface.modelClass
        link:                  Link  = Link('', linkType=LinkType.INTERFACE, source=implementorModelClass, destination=interfaceModelClass)

        umlInterface: UmlInterface = UmlInterface(link=link, interfaceClass=interface, implementingClass=implementation)
        umlInterface.umlFrame = self._umlFrame
        umlInterface.MakeLineControlPoints(n=2)

        implementation.addLink(umlLink=umlInterface, destinationClass=interface)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInterface, previousEventHandler=umlInterface.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlInterface.SetEventHandler(eventHandler)

        return umlInterface

    def _createNoteLink(self) -> UmlNoteLink:

        sourceNote:       UmlNote  = cast(UmlNote, self._sourceUmlShape)                # noqa
        destinationClass: UmlClass = cast(UmlClass, self._destinationUmlShape)          # noqa

        sourceModelNote:       Note  = sourceNote.modelNote
        destinationModelClass: Class = destinationClass.modelClass

        # If none, we are creating from scratch
        # If we have a value, we are undoing a delete action
        if self._modelLink is None:
            link: Link  = Link("", linkType=LinkType.NOTELINK, source=sourceModelNote, destination=destinationModelClass)
        else:
            link = self._modelLink

        umlNoteLink: UmlNoteLink = UmlNoteLink(link=link)
        umlNoteLink.sourceNote       = sourceNote
        umlNoteLink.destinationClass = destinationClass
        umlNoteLink.umlPubSubEngine  = self._umlPubSubEngine
        umlNoteLink.umlFrame         = self._umlFrame
        umlNoteLink.MakeLineControlPoints(2)

        sourceNote.addLink(umlNoteLink=umlNoteLink, umlClass=destinationClass)

        eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink, previousEventHandler=umlNoteLink.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlNoteLink.SetEventHandler(eventHandler)

        return umlNoteLink

    def _getAppropriateAssociation(self, link: Link) -> UmlAssociationGenre:
        if self._linkType == LinkType.ASSOCIATION:
            return UmlAssociation(link=link)
        elif self._linkType == LinkType.AGGREGATION:
            return UmlAggregation(link=link)
        elif self._linkType == LinkType.COMPOSITION:
            return UmlComposition(link=link)
        else:
            assert False, 'Unknown association'

    def _getAppropriateModelLink(self, source: UmlClass, destination: UmlClass) -> Link:
        """

        Args:
            source:
            destination:

        Returns:  The correct model link instance
        """

        linkType: LinkType = self._linkType

        # If none, we are creating from scratch
        # If we have a value, we are undoing a delete action
        if self._modelLink is None:
            link: Link = Link(name="", linkType=linkType, source=source.modelClass, destination=destination.modelClass)
            link.name = f'{linkType.name.capitalize()}-{link.id}'
        else:
            link = self._modelLink

        return link

    def _toCommandName(self, linkType: LinkType) -> str:
        # Because I do not like the generated name
        if linkType == LinkType.SD_MESSAGE:
            return f'SDMessage Link'
        else:
            return f'{linkType.name.capitalize()} Link'

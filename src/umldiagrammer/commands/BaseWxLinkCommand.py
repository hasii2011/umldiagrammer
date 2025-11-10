
from typing import Dict
from typing import cast
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import OK
from wx import Point
from wx import ICON_ERROR

from wx import Command
from wx import MessageDialog

from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutClass import PyutClass

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

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
                 linkType:    PyutLinkType,
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

        self._linkType: PyutLinkType = linkType

        self._srcPoint: Point = cast(Point, None)
        self._dstPoint: Point = cast(Point, None)

        self._link:     UmlLink  = cast(UmlLink, None)
        self._pyutLink: PyutLink = cast(PyutLink, None)    # for undo of delete
        self._spline:   bool     = False
        # self._controlPoints: ControlPoints = ControlPoints([])       # for undo of delete or create link from plugin manager

        #
        # Dispatch table, aka dictionary
        #
        self._linkCreationDispatcher: Dict[PyutLinkType, Callable] = {
            PyutLinkType.INHERITANCE: self._createInheritanceLink,
            PyutLinkType.INTERFACE:   self._createInterfaceLink,
            PyutLinkType.ASSOCIATION: self._createAssociationLink,
            PyutLinkType.NOTELINK:    self._createNoteLink,
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
            umlAssociation: UmlAssociation = cast(UmlAssociation, link)
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
        linkType: PyutLinkType = self._linkType
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
        sourceClass:      UmlClass = cast(UmlClass, self._sourceUmlShape)
        destinationClass: UmlClass = cast(UmlClass, self._destinationUmlShape)

        linkType: PyutLinkType = self._linkType

        # If none, we are creating from scratch
        # If we have a value, we are undoing a delete action
        if self._pyutLink is None:
            pyutLink: PyutLink = PyutLink(name="", linkType=linkType, source=sourceClass.pyutClass, destination=destinationClass.pyutClass)
            pyutLink.name = f'{linkType.name.capitalize()}-{pyutLink.id}'
        else:
            pyutLink = self._pyutLink

        umlAssociation: UmlAssociationGenre = self._getAppropriateAssociation(pyutLink=pyutLink)

        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.umlFrame = self._umlFrame
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceClass.addLink(umlLink=umlAssociation, destinationClass=destinationClass)
        # add it to the source PyutClass
        sourceClass.pyutClass.addLink(pyutLink)

        # Update the model
        srcClassPyutClass: PyutClass = sourceClass.pyutClass
        destPyutClass:     PyutClass = destinationClass.pyutClass
        destPyutClass.addParent(srcClassPyutClass)
        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation)

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

        self._name = self._toCommandName(linkType)

        return umlAssociation

    def _createInheritanceLink(self) -> UmlInheritance:
        """
        source == SubClass
        destination == Base Class.  (arrow here)

        Add a parent link between the child and parent objects.

        Returns:
            The inheritance UmlLink
        """
        subClass:  UmlClass = cast(UmlClass, self._sourceUmlShape)
        baseClass: UmlClass = cast(UmlClass, self._destinationUmlShape)

        sourceModelClass:      PyutClass = cast(PyutClass, subClass.pyutClass)
        destinationModelClass: PyutClass = cast(PyutClass, baseClass.pyutClass)
        # If none, we are creating from scratch
        # If we have a value, we are undoing a delete action
        if self._pyutLink is None:
            pyutLink: PyutLink  = PyutLink("", linkType=PyutLinkType.INHERITANCE, source=sourceModelClass, destination=destinationModelClass)
        else:
            pyutLink = self._pyutLink

        umlLink: UmlInheritance = UmlInheritance(pyutLink=pyutLink, baseClass=baseClass, subClass=subClass)
        umlLink.umlFrame = self._umlFrame
        umlLink.MakeLineControlPoints(n=2)       # Make this configurable

        subClass.addLink(umlLink=umlLink, destinationClass=baseClass)

        # Update the model
        subClassPyutClass: PyutClass = subClass.pyutClass
        basePyutClass:     PyutClass = baseClass.pyutClass

        subClassPyutClass.addParent(basePyutClass)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlLink)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlLink.GetEventHandler())
        umlLink.SetEventHandler(eventHandler)

        return umlLink

    def _createInterfaceLink(self) -> UmlInterface:

        interface:      UmlClass = cast(UmlClass, self._destinationUmlShape)
        implementation: UmlClass = cast(UmlClass, self._sourceUmlShape)

        implementorModelClass: PyutClass = implementation.pyutClass
        interfaceModelClass:   PyutClass = interface.pyutClass
        pyutLink:              PyutLink  = PyutLink('', linkType=PyutLinkType.INTERFACE, source=implementorModelClass, destination=interfaceModelClass)

        umlInterface: UmlInterface = UmlInterface(pyutLink=pyutLink, interfaceClass=interface, implementingClass=implementation)
        umlInterface.umlFrame = self._umlFrame
        umlInterface.MakeLineControlPoints(n=2)

        implementation.addLink(umlLink=umlInterface, destinationClass=interface)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInterface)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlInterface.GetEventHandler())
        umlInterface.SetEventHandler(eventHandler)

        return umlInterface

    def _createNoteLink(self) -> UmlNoteLink:

        sourceNote:       UmlNote  = cast(UmlNote, self._sourceUmlShape)
        destinationClass: UmlClass = cast(UmlClass, self._destinationUmlShape)

        sourceModelClass:      PyutNote  = cast(PyutNote,  sourceNote.pyutNote)
        destinationModelClass: PyutClass = cast(PyutClass, destinationClass.pyutClass)

        # If none, we are creating from scratch
        # If we have a value, we are undoing a delete action
        if self._pyutLink is None:
            pyutLink: PyutLink  = PyutLink("", linkType=PyutLinkType.NOTELINK, source=sourceModelClass, destination=destinationModelClass)
        else:
            pyutLink = self._pyutLink

        umlNoteLink: UmlNoteLink = UmlNoteLink(pyutLink=pyutLink)
        umlNoteLink.sourceNote       = sourceNote
        umlNoteLink.destinationClass = destinationClass
        umlNoteLink.umlPubSubEngine  = self._umlPubSubEngine
        umlNoteLink.umlFrame         = self._umlFrame
        umlNoteLink.MakeLineControlPoints(2)

        sourceNote.addLink(umlNoteLink=umlNoteLink, umlClass=destinationClass)

        eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlNoteLink.GetEventHandler())
        umlNoteLink.SetEventHandler(eventHandler)

        return umlNoteLink

    def _getAppropriateAssociation(self, pyutLink: PyutLink) -> UmlAssociationGenre:
        if self._linkType == PyutLinkType.ASSOCIATION:
            return UmlAssociation(pyutLink=pyutLink)
        elif self._linkType == PyutLinkType.AGGREGATION:
            return UmlAggregation(pyutLink=pyutLink)
        elif self._linkType == PyutLinkType.COMPOSITION:
            return UmlComposition(pyutLink=pyutLink)
        else:
            assert False, 'Unknown association'

    def _toCommandName(self, linkType: PyutLinkType) -> str:
        # Because I do not like the generated name
        if linkType == PyutLinkType.SD_MESSAGE:
            return f'SDMessage Link'
        else:
            return f'{linkType.name.capitalize()} Link'

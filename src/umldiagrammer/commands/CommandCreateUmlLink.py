
from logging import Logger
from logging import getLogger

from wx import Yield as wxYield

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umldiagrammer.DiagrammerTypes import UmlShapeGenre
from umldiagrammer.commands.BaseWxLinkCommand import BaseWxLinkCommand

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine


class CommandCreateUmlLink(BaseWxLinkCommand):

    def __init__(self,
                 umlFrame: UmlFrame,
                 appPubSubEngine: IAppPubSubEngine,
                 umlPubSubEngine: IUmlPubSubEngine,
                 source:       UmlShapeGenre,
                 destination:  UmlShapeGenre,
                 linkType: PyutLinkType = PyutLinkType.INHERITANCE
                 ):
        """
        Lollipop Interface
        ------------------
        Destination == Implementing Class


        Inheritance Link
        ----------------
        source == SubClass
        destination == Base Class.  (arrow to here)

        Interface Link
        ----------------
        source == Implementing cass
        destination == Interface class (arrow to here)

        Note Links
        ----------
        source == Note
        destination == UmlClass


        Association Links
        ----------------
        source has the diamond


        Args:
            umlFrame:           The frame which we will create a UML Link
            appPubSubEngine:    Application publish/subscribe engine
            umlPubSubEngine:    The UML Shapes publish/subscribe engine
            source:                The source of the link
            destination:                The destination of the link
            linkType:           The type of link
        """
        super().__init__(partialName='Create', linkType=linkType,
                         umlFrame=umlFrame,
                         appPubSubEngine=appPubSubEngine,
                         umlPubSubEngine=umlPubSubEngine
                         )

        self.logger: Logger = getLogger(__name__)

        self._sourceUmlShape      = source
        self._destinationUmlShape = destination

    def Do(self) -> bool:
        self._link = self._createLink()
        self._cbPlaceLink()
        return True

    def Undo(self) -> bool:
        """
        Returns:  True to indicate the undo was done
        """
        self.logger.info(f'Undo Create: {self._link}')

        self._cbDoDeleteLink()

        wxYield()

        return True


from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutClass import PyutClass

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPosition

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.commands.BaseWxCreateCommand import BaseWxCreateCommand

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


class CommandCreateUmlClass(BaseWxCreateCommand):

    clsCounter: int = 1

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):
        """
        If the caller provides a ready-made class this command uses it and does not
        invoke the class editor

        Args:
            umlPosition:
            umlPubSubEngine:
        """
        name: str = f'Create Class- {CommandCreateUmlClass.clsCounter}'
        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        self._umlFrame: UmlFrame = umlFrame

        self.logger: Logger = getLogger(__name__)

    def Undo(self) -> bool:

        self.logger.info(f'{self._umlFrame=}')
        # SD Instance will not appear here
        assert isinstance(self._shape, UmlClass), 'It can only be this for this command'
        umlClass:  UmlClass  = cast(UmlClass, self._shape)
        pyutClass: PyutClass = umlClass.pyutClass
        self._removeUmlShapeFromFrame(umlFrame=self._umlFrame, umlShape=self._shape, pyutClass=pyutClass)

        return True

    def _createPrototypeInstance(self) -> UmlClass:
        """
        Creates an appropriate class for the new command

        Returns:    The newly created class
        """
        """
        Implement required abstract method

        Create a new class

        Returns: the newly created OglClass
        """
        className: str       = f'{self._umlPreferences.defaultClassName}{CommandCreateUmlClass.clsCounter}'
        pyutClass: PyutClass = PyutClass(name=className)
        umlClass:  UmlClass  = UmlClass(pyutClass)

        CommandCreateUmlClass.clsCounter += 1

        return umlClass

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlClass:  UmlClass  = cast(UmlClass, self._shape)              # get old
        pyutClass: PyutClass = umlClass.pyutClass

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlClass, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._appPubSubEngine.sendMessage(messageType=MessageType.EDIT_CLASS, uniqueId=APPLICATION_FRAME_ID, umlFrame=self._umlFrame, pyutClass=pyutClass)

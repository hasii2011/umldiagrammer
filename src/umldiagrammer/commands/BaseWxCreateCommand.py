
from logging import Logger
from logging import getLogger

from abc import ABCMeta
from abc import abstractmethod
from typing import cast

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler

from umlshapes.types.UmlPosition import UmlPosition

from umldiagrammer.DiagrammerTypes import UmlShapeGenre

from umldiagrammer.commands.BaseWxCommand import BaseWxCommand
from umldiagrammer.commands.CommandTypes import DoableObjectType

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine


class MyMetaBaseWxCommand(ABCMeta, type(BaseWxCommand)):        # type: ignore
    """
    I have no idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass

# noinspection PyAbstractClass
class BaseWxCreateCommand(BaseWxCommand, metaclass=MyMetaBaseWxCommand):
    """
    Did now inspection because was not catch that we are an ABC
    """
    def __init__(self, canUndo: bool, name: str, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine, umlFrame: UmlFrame, umlPosition: UmlPosition):

        super().__init__(canUndo=canUndo, name=name, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        self._baseWxCreateLogger: Logger      = getLogger(__name__)
        self._umlFrame:           UmlFrame    = umlFrame
        self._umlPosition:        UmlPosition = umlPosition

        self._shape: DoableObjectType = self._createPrototypeInstance()

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True

    def Do(self) -> bool:
        self._placeShapeOnFrame()
        return True

    def Undo(self) -> bool:
        # self._eventEngine.sendEvent(EventType.ActiveUmlFrame, callback=self._cbGetActiveUmlFrameForUndo)

        from umlshapes.frames.DiagramFrame import DiagramFrame
        from umlshapes.UmlDiagram import UmlDiagram

        umlFrame:   DiagramFrame = self._umlFrame
        umlDiagram: UmlDiagram   = umlFrame.umlDiagram

        self._baseWxCreateLogger.info(f'Undo create {self._shape}')
        umlDiagram.RemoveShape(self._shape)
        umlFrame.refresh()

        return True

    @abstractmethod
    def _createPrototypeInstance(self) -> DoableObjectType:
        """
        Creates an appropriate class for the new command

        Returns:    The newly created class
        """
        pass

    @abstractmethod
    def _placeShapeOnFrame(self):
        """
        Implemented by subclasses to support .Do
        """
        pass

    def _addUmlShapeToFrame(self, umlFrame: UmlFrame, umlShape: UmlShapeGenre, umlPosition: UmlPosition):
        """
        This is common code needed to create Note, Text, Actor, and UseCase shapes.

        Args:
            umlFrame:
            umlShape:
            umlPosition:
        """
        self._baseWxCreateLogger.debug(f'{umlFrame=}')

        umlShape.position = umlPosition
        umlDiagram: UmlDiagram = umlFrame.umlDiagram
        umlDiagram.AddShape(umlShape)

        umlShape.Show(show=True)

        eventHandler: UmlBaseEventHandler = cast(UmlBaseEventHandler, None)
        if isinstance(umlShape, UmlClass):
            eventHandler = UmlClassEventHandler()
        elif isinstance(umlShape, UmlNote):
            eventHandler = UmlNoteEventHandler()
        elif isinstance(umlShape, UmlText):
            eventHandler = UmlTextEventHandler()
        else:
            pass

        if eventHandler is not None:
            eventHandler.SetShape(umlShape)
            eventHandler.umlPubSubEngine = self._umlPubSubEngine
            eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
            umlShape.SetEventHandler(eventHandler)

        umlFrame.refresh()

        self._baseWxCreateLogger.info(f'Created {self._shape}')


from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutNote import PyutNote

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.types.UmlPosition import UmlPosition

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.commands.BaseWxCreateCommand import BaseWxCreateCommand
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


class CommandCreateUmlNote(BaseWxCreateCommand):

    clsCounter: int = 1

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        name: str = f'Create Class- {CommandCreateUmlNote.clsCounter}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def _createPrototypeInstance(self) -> UmlNote:
        """
        Creates an appropriate class for the new command

        Returns:    The newly created class
        """
        noteName: str = f'{self._umlPreferences.defaultClassName}{CommandCreateUmlNote.clsCounter}'

        pyutNote: PyutNote = PyutNote(content=self._umlPreferences.noteText)
        pyutNote.name = noteName        # Do we really need this

        umlClass: UmlNote  = UmlNote(pyutNote)

        CommandCreateUmlNote.clsCounter += 1

        return umlClass

    def _placeShapeOnFrame(self):

        """
        Place self._shape on the UML frame
        """
        umlNote:  UmlNote  = cast(UmlNote, self._shape)              # get old
        pyutNote: PyutNote = umlNote.pyutNote

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlNote, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._appPubSubEngine.sendMessage(messageType=MessageType.EDIT_NOTE, uniqueId=APPLICATION_FRAME_ID, umlFrame=self._umlFrame, pyutNote=pyutNote)

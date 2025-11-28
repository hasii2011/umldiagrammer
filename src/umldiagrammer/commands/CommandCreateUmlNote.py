
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.Note import Note

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
        Creates an appropriate UML shape for the new command

        Returns:    The newly created note
        """
        noteName: str = f'UmlNote{CommandCreateUmlNote.clsCounter}'

        modelNote: Note = Note(content=self._umlPreferences.noteText)
        modelNote.name = noteName        # Do we really need this

        umlNote: UmlNote  = UmlNote(modelNote)

        CommandCreateUmlNote.clsCounter += 1

        return umlNote

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlNote:   UmlNote = cast(UmlNote, self._shape)              # get old
        modelNote: Note    = umlNote.modelNote

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlNote, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._appPubSubEngine.sendMessage(messageType=MessageType.EDIT_NOTE, uniqueId=APPLICATION_FRAME_ID, umlFrame=self._umlFrame, note=modelNote)

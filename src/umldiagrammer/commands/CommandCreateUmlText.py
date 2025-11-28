
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.Text import Text

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.UmlText import UmlText

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.commands.BaseWxCreateCommand import BaseWxCreateCommand

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


class CommandCreateUmlText(BaseWxCreateCommand):

    clsCounter: int = 1

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        name: str = f'Create Class- {CommandCreateUmlText.clsCounter}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def _createPrototypeInstance(self) -> UmlText:
        """
        Creates an appropriate UML shape for the new command

        Returns:    The newly created text
        """
        textName: str = f'UmlText-{CommandCreateUmlText.clsCounter}'

        text: Text = Text(content=self._umlPreferences.textValue)
        text.name = textName        # Do we really need this

        umlText: UmlText = UmlText(text)

        CommandCreateUmlText.clsCounter += 1

        return umlText

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlText:   UmlText = cast(UmlText, self._shape)              # get old
        modelText: Text    = umlText.modelText

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlText, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._appPubSubEngine.sendMessage(messageType=MessageType.EDIT_TEXT, uniqueId=APPLICATION_FRAME_ID, umlFrame=self._umlFrame, text=modelText)

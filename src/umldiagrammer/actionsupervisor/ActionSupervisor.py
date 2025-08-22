
from typing import Dict
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Command
from wx import ICON_ERROR
from wx import OK

from wx import MessageDialog

from codeallybasic.SingletonV3 import SingletonV3

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umldiagrammer.UIAction import UIAction
from umldiagrammer.UIIdentifiers import UIIdentifiers
from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.commands.CommandCreateUmlClass import CommandCreateUmlClass

from umldiagrammer.pubsubengine.MessageType import MessageType
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

CLICK:    str = 'Click'
LOCATION: str = f'{CLICK} to place the new'
ON:       str = f'{CLICK} on the'
INSIDE:   str = f'{CLICK} inside the lifeline of the'

MESSAGES: Dict[UIAction, str] = {
    UIAction.SELECTOR:                     'Ready',
    UIAction.NEW_CLASS:                    f'{LOCATION} class',
    UIAction.NEW_NOTE:                     f'{LOCATION} note',
    UIAction.NEW_ACTOR:                    f'{LOCATION} actor',
    UIAction.NEW_TEXT:                     f'{LOCATION} text',
    UIAction.NEW_USECASE:                  f'{LOCATION} case',
    UIAction.NEW_SD_INSTANCE:              f'{LOCATION} instance',
    UIAction.NEW_SD_MESSAGE:               f'{INSIDE} caller',
    UIAction.DESTINATION_SD_MESSAGE:       f'{INSIDE} message implementer',
    UIAction.NEW_IMPLEMENT_LINK:           f'{ON} interface implementor',
    UIAction.NEW_INHERIT_LINK:             f'{ON} subclass',
    UIAction.NEW_AGGREGATION_LINK:         f'{ON} aggregator',
    UIAction.NEW_COMPOSITION_LINK:         f'{ON} composer',
    UIAction.NEW_ASSOCIATION_LINK:         f'{ON} source of the association',
    UIAction.NEW_NOTE_LINK:                f'{ON} note',
    UIAction.DESTINATION_IMPLEMENT_LINK:   f'{ON} interface',
    UIAction.DESTINATION_INHERIT_LINK:     f'{ON} parent class',
    UIAction.DESTINATION_AGGREGATION_LINK: f'{ON} "aggregated" class',
    UIAction.DESTINATION_COMPOSITION_LINK: f'{ON} "composed" class',
    UIAction.DESTINATION_ASSOCIATION_LINK: f'{ON} destination of the association',
    UIAction.DESTINATION_NOTE_LINK:        f'{ON} class',
}


class ActionSupervisor(metaclass=SingletonV3):
    def __init__(self, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: UmlPubSubEngine):

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: UmlPubSubEngine  = umlPubSubEngine

        self.logger:          Logger          = getLogger(__name__)

        self._currentAction:           UIAction = UIAction.SELECTOR
        self._currentActionPersistent: bool     = False

    @property
    def currentAction(self) -> UIAction:
        return self._currentAction

    @currentAction.setter
    def currentAction(self, action: UIAction):
        """
        This tells the action handler which action to do for the next doAction call.

        Args:
            action:  the action from ACTION enumeration
        """
        self.logger.debug(f'Set current action to: {action}')
        if self._currentAction == action:
            self._currentActionPersistent = True
        else:
            self._currentAction = action
            self._currentActionPersistent = False

        # self.setStatusText(MESSAGES[self._currentAction])
        msg: str = MESSAGES[self._currentAction]
        self._setStatusText(msg)

    def registerNewFrame(self, frameId: FrameId):
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.FRAME_LEFT_CLICK, frameId=frameId, callback=self._onFrameClick)

    def doAction(self, umlFrame: UmlFrame, umlPosition: UmlPosition):
        """
        Do the current action at coordinates x, y.

        Args:
            umlFrame:  The frame we are acting on
            umlPosition
        """
        self.logger.debug(f'doAction: {self._currentAction}  {UIAction.SELECTOR=}')
        self._resetStatusText()

        currentAction: UIAction  = self._currentAction

        cmd: Command = cast(Command, None)

        match currentAction:
            case UIAction.SELECTOR:
                pass
            case UIAction.NEW_CLASS:
                if self._isThisLegalClassDiagramAction(umlFrame=umlFrame) is True:
                    self.logger.info(f'Create Class on frame: {umlFrame.id} at {umlPosition=}')
                    cmd = CommandCreateUmlClass(umlFrame=umlFrame, umlPosition=umlPosition, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)

        if cmd is not None:
            self._resetToActionSelector()
            submitStatus: bool = umlFrame.commandProcessor.Submit(command=cmd, storeIt=True)
            self.logger.debug(f'Create command submission status: {submitStatus}')

    def _onFrameClick(self, frame: UmlFrame, umlPosition: UmlPosition):
        self.logger.info(f'{frame.id=} {umlPosition=}')
        self.doAction(umlFrame=frame, umlPosition=umlPosition)

    def _resetStatusText(self):
        self._setStatusText('')

    def _setStatusText(self, msg: str):
        self._appPubSubEngine.sendMessage(messageType=MessageType.UPDATE_APPLICATION_STATUS_MSG, uniqueId=APPLICATION_FRAME_ID, message=msg)

    def _isThisLegalUseCaseDiagramAction(self, umlFrame) -> bool:

        from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame
        if isinstance(umlFrame, UseCaseDiagramFrame):
            return True
        else:
            self._displayError(title='Please create a use case diagram.', message='A use case symbol can only be added to a use case diagram.')
            return False

    def _isThisLegalClassDiagramAction(self, umlFrame) -> bool:

        from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
        if isinstance(umlFrame, ClassDiagramFrame):
            return True
        else:
            self._displayError(title='Please create a class diagram.', message='This symbol can only be added to a class diagram.')
            return False

    def _displayError(self, title: str, message: str):

        with MessageDialog(parent=None, message=message, caption=title, style=OK | ICON_ERROR) as dlg:
            dlg.ShowModal()

    def _resetToActionSelector(self):
        """
        For non-persistent tools
        """
        if not self._currentActionPersistent:
            self._currentAction = UIAction.SELECTOR
            self._selectTool(UIIdentifiers.ID_ARROW)

    def _selectTool(self, toolId: int):
        """
        Select the tool of given ID from the toolbar, and deselect the others.

        Args:
            toolId:  The tool id
        """
        self._appPubSubEngine.sendMessage(MessageType.SELECT_TOOL, uniqueId=APPLICATION_FRAME_ID, toolId=toolId)
        # self._eventEngine.sendEvent(EventType.SelectTool, toolId=toolId)

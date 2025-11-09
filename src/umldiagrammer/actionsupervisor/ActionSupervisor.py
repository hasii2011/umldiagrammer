
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import ICON_ERROR
from wx import ICON_WARNING
from wx import OK

from wx import Command
from wx import MessageDialog

from codeallybasic.SingletonV3 import SingletonV3

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.types.UmlPosition import UmlPosition

from umldiagrammer.UIAction import UIAction
from umldiagrammer.UIIdentifiers import UIIdentifiers

from umldiagrammer.DiagrammerTypes import UmlShapeGenre
from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.commands.CommandCreateUmlClass import CommandCreateUmlClass
from umldiagrammer.commands.CommandCreateUmlLink import CommandCreateUmlLink
from umldiagrammer.commands.CommandCreateUmlNote import CommandCreateUmlNote
from umldiagrammer.commands.CommandCreateUmlText import CommandCreateUmlText
from umldiagrammer.commands.CommandCreateLollipopInterface import CommandCreateLollipopInterface

from umldiagrammer.data.LollipopCreationData import LollipopCreationData

from umldiagrammer.pubsubengine.MessageType import MessageType
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

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
    UIAction.DESTINATION_INHERIT_LINK:     f'{ON} base class',
    UIAction.DESTINATION_AGGREGATION_LINK: f'{ON} "aggregated" class',
    UIAction.DESTINATION_COMPOSITION_LINK: f'{ON} "composed" class',
    UIAction.DESTINATION_ASSOCIATION_LINK: f'{ON} destination of the association',
    UIAction.DESTINATION_NOTE_LINK:        f'{ON} class',
}

NONE_UML_OBJECT: UmlShapeGenre = cast(UmlShapeGenre, None)

UIActions = NewType('UIActions', List[UIAction])

# list of actions which are source events
SOURCE_ACTIONS: UIActions = UIActions([
    UIAction.NEW_IMPLEMENT_LINK,
    UIAction.NEW_INHERIT_LINK,
    UIAction.NEW_AGGREGATION_LINK,
    UIAction.NEW_COMPOSITION_LINK,
    UIAction.NEW_ASSOCIATION_LINK,
    UIAction.NEW_NOTE_LINK,
    UIAction.NEW_SD_MESSAGE,
])

# list of actions which are destination events
DESTINATION_ACTIONS: UIActions = UIActions([
    UIAction.DESTINATION_IMPLEMENT_LINK,
    UIAction.DESTINATION_INHERIT_LINK,
    UIAction.DESTINATION_AGGREGATION_LINK,
    UIAction.DESTINATION_COMPOSITION_LINK,
    UIAction.DESTINATION_ASSOCIATION_LINK,
    UIAction.DESTINATION_NOTE_LINK,
    UIAction.DESTINATION_SD_MESSAGE,
])

# a dictionary of the next action to select
NEXT_ACTION = {
    UIAction.SELECTOR:                 UIAction.SELECTOR,
    UIAction.NEW_CLASS:                UIAction.SELECTOR,
    UIAction.NEW_NOTE:                 UIAction.SELECTOR,
    UIAction.NEW_IMPLEMENT_LINK:          UIAction.DESTINATION_IMPLEMENT_LINK,
    UIAction.NEW_INHERIT_LINK:            UIAction.DESTINATION_INHERIT_LINK,
    UIAction.NEW_AGGREGATION_LINK:        UIAction.DESTINATION_AGGREGATION_LINK,
    UIAction.NEW_COMPOSITION_LINK:        UIAction.DESTINATION_COMPOSITION_LINK,
    UIAction.NEW_ASSOCIATION_LINK:        UIAction.DESTINATION_ASSOCIATION_LINK,
    UIAction.NEW_NOTE_LINK:               UIAction.DESTINATION_NOTE_LINK,
    UIAction.DESTINATION_IMPLEMENT_LINK:  UIAction.SELECTOR,

    UIAction.DESTINATION_INHERIT_LINK:     UIAction.SELECTOR,
    UIAction.DESTINATION_AGGREGATION_LINK: UIAction.SELECTOR,
    UIAction.DESTINATION_COMPOSITION_LINK: UIAction.SELECTOR,
    UIAction.DESTINATION_ASSOCIATION_LINK: UIAction.SELECTOR,
    UIAction.DESTINATION_NOTE_LINK:        UIAction.SELECTOR,
    UIAction.NEW_ACTOR:                    UIAction.SELECTOR,
    UIAction.NEW_USECASE:                  UIAction.SELECTOR,

    UIAction.NEW_SD_INSTANCE: UIAction.SELECTOR,
    UIAction.NEW_SD_MESSAGE:  UIAction.DESTINATION_SD_MESSAGE,
}

UML_RELATIONSHIP_ACTIONS: UIActions = UIActions([
    UIAction.NEW_INHERIT_LINK,
    UIAction.NEW_AGGREGATION_LINK,
    UIAction.NEW_COMPOSITION_LINK,
    UIAction.NEW_IMPLEMENT_LINK,
    UIAction.NEW_ASSOCIATION_LINK,
])

UML_RELATIONSHIP_LINK_ACTIONS: UIActions = UIActions([
    UIAction.DESTINATION_IMPLEMENT_LINK,
    UIAction.DESTINATION_INHERIT_LINK,
    UIAction.DESTINATION_AGGREGATION_LINK,
    UIAction.DESTINATION_COMPOSITION_LINK,
    UIAction.DESTINATION_ASSOCIATION_LINK,
])

UI_ACTION_TO_LINK_TYPE = {
    UIAction.DESTINATION_IMPLEMENT_LINK:     PyutLinkType.INTERFACE,
    UIAction.DESTINATION_INHERIT_LINK:       PyutLinkType.INHERITANCE,
    UIAction.DESTINATION_AGGREGATION_LINK:   PyutLinkType.AGGREGATION,
    UIAction.DESTINATION_COMPOSITION_LINK:   PyutLinkType.COMPOSITION,
    UIAction.DESTINATION_ASSOCIATION_LINK:   PyutLinkType.ASSOCIATION,
    UIAction.DESTINATION_NOTE_LINK:          PyutLinkType.NOTELINK,
    UIAction.DESTINATION_SD_MESSAGE:         PyutLinkType.SD_MESSAGE,
}


@dataclass
class ValidationResult:
    isValid:      bool = True
    errorMessage: str = ''


class ActionSupervisor(metaclass=SingletonV3):
    """
    This class handles the user interactions with the frames.  Thus shapes are created
    here (via Commands)
    """
    def __init__(self, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self.logger: Logger = getLogger(__name__)

        self._currentAction:           UIAction = UIAction.SELECTOR
        self._currentActionPersistent: bool     = False

        self._source:      UmlShapeGenre = NONE_UML_OBJECT
        self._destination: UmlShapeGenre = NONE_UML_OBJECT

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
        self.logger.info(f'Set current action to: {action}')
        if self._currentAction == action:
            self._currentActionPersistent = True
        else:
            self._currentAction = action
            self._currentActionPersistent = False

        msg: str = MESSAGES[self._currentAction]
        self._setStatusText(msg)

    def registerNewFrame(self, frameId: FrameId):
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.FRAME_LEFT_CLICK,   frameId=frameId, listener=self._frameClickListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.UML_SHAPE_SELECTED, frameId=frameId, listener=self._shapeSelectedListener)

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
            case UIAction.NEW_NOTE:
                if self._isThisLegalClassDiagramAction(umlFrame=umlFrame) is True:
                    cmd = CommandCreateUmlNote(umlFrame=umlFrame, umlPosition=umlPosition, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)
            case UIAction.NEW_TEXT:
                cmd = CommandCreateUmlText(umlFrame=umlFrame, umlPosition=umlPosition, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)

        if cmd is not None:
            self._resetToActionSelector()
            submitStatus: bool = umlFrame.commandProcessor.Submit(command=cmd, storeIt=True)
            self.logger.debug(f'Create command submission status: {submitStatus}')

    def createLollipopInterface(self, lollipopCreationData: LollipopCreationData):
        """
        Done here because this is where we do this

        Args:
            lollipopCreationData:

        """
        umlFrame: UmlFrame = lollipopCreationData.requestingFrame
        command: CommandCreateLollipopInterface = CommandCreateLollipopInterface(
            appPubSubEngine=self._appPubSubEngine,
            umlPubSubEngine=self._umlPubSubEngine,
            creationData=lollipopCreationData
        )

        self._resetToActionSelector()
        submitStatus: bool = umlFrame.commandProcessor.Submit(command=command, storeIt=True)
        self.logger.debug(f'Create command submission status: {submitStatus}')

    def _frameClickListener(self, frame: UmlFrame, umlPosition: UmlPosition):
        self.logger.info(f'{frame.id=} {umlPosition=}')
        self.doAction(umlFrame=frame, umlPosition=umlPosition)

    def _shapeSelectedListener(self, umlShape):
        self.logger.info(f'{self._currentAction=} {umlShape}')

        assert umlShape is not None, 'This should not happen since shape layer sent this message'

        if self._currentAction in SOURCE_ACTIONS:
            self._attemptSourceAction(umlShape)
        elif self._currentAction in DESTINATION_ACTIONS:
            self._attemptDestinationAction(umlShape=umlShape)
        else:
            self._setStatusText("Error : Action not supported by the Action Handler")
            return

        self._setStatusText(MESSAGES[self._currentAction])

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

    def _attemptSourceAction(self, umlShape: UmlShapeGenre):
        """

        Args:
            umlShape: The shape the user clicked on

        """
        result: ValidationResult = self._validateSourceAction(umlShape=umlShape)
        if result.isValid is True:
            if self._currentActionPersistent:
                self._oldAction = self._currentAction
            self._currentAction = NEXT_ACTION[self._currentAction]

            self.logger.debug(f'Save source - shape {umlShape}')
            self._source    = umlShape
        else:
            with MessageDialog(parent=None, message=result.errorMessage, caption='Invalid Source', style=OK | ICON_WARNING) as dlg:
                dlg.ShowModal()

            self._cancelAction(msg='Invalid Source')

    def _attemptDestinationAction(self, umlShape: UmlShapeGenre):
        """
        We either create link or show a warning message
        Args:
            umlShape:
        """
        result: ValidationResult = self._validateDestinationAction(umlShape=umlShape)
        if result.isValid is True:
            self._destination = umlShape

            command:  CommandCreateUmlLink = self._createLinkCommand()
            umlFrame: UmlFrame             = self._source.umlFrame

            umlFrame.commandProcessor.Submit(command=command, storeIt=True)

            self._source = NONE_UML_OBJECT
            self._destination = NONE_UML_OBJECT

            if self._currentActionPersistent:
                self._currentAction = self._oldAction
            else:
                self._currentAction = UIAction.SELECTOR
                self._selectActionSelectorTool()
        else:
            with MessageDialog(parent=None, message=result.errorMessage, caption='Invalid Destination', style=OK | ICON_WARNING) as dlg:
                dlg.ShowModal()

            self._cancelAction(msg='Invalid Destination')

    def _validateSourceAction(self, umlShape: UmlShapeGenre) -> ValidationResult:

        result: ValidationResult = ValidationResult()

        if self._currentAction == UIAction.NEW_NOTE_LINK and not isinstance(umlShape, UmlNote):
            result.isValid      = False
            result.errorMessage = 'Source of note link must be a note'
        elif self._currentAction == UIAction.NEW_ASSOCIATION_LINK and isinstance(umlShape, UmlActor):
            pass
        elif self._currentAction in UML_RELATIONSHIP_ACTIONS:
            if not isinstance(umlShape, UmlShapeGenre):
                result.isValid      = False
                result.errorMessage = 'UML relationships must start at a class'

        return result

    def _validateDestinationAction(self, umlShape: UmlShapeGenre) -> ValidationResult:
        """
        For links that do not belong in a class diagram we do nothing and just
        return and error

        Args:
            umlShape:

        Returns:  The results of the validation
        """

        result: ValidationResult = ValidationResult()

        if self._currentAction == UIAction.DESTINATION_ASSOCIATION_LINK and isinstance(umlShape, UmlUseCase):
            pass
        # elif self._currentAction == UIAction.DESTINATION_ASSOCIATION_LINK and isinstance(umlShape, UmlSDInstance):
        #     pass
        elif self._currentAction in UML_RELATIONSHIP_LINK_ACTIONS:
            if not isinstance(umlShape, UmlClass):
                result.isValid      = False
                result.errorMessage = 'UML relationships must end at a class'
        elif self._currentAction == UIAction.DESTINATION_NOTE_LINK and (isinstance(umlShape, UmlNote) or isinstance(umlShape, UmlText)):
            result.isValid = False
            result.errorMessage = 'Note to Note or Note to Text\nassociations not allowed'

        return result

    def _cancelAction(self, msg: str):

        self.logger.info(f'{msg}')
        self._currentAction = UIAction.SELECTOR
        self._selectActionSelectorTool()
        self._setStatusText(f'{msg}')

    def _selectActionSelectorTool(self):
        self._selectTool(UIIdentifiers.ID_ARROW)

    def _createLinkCommand(self) -> CommandCreateUmlLink:

        assert self._source is not None, 'Developer error: The link source is not set'
        assert self._destination is not None, 'Developer error: The link destination is not set'
        linkType: PyutLinkType = UI_ACTION_TO_LINK_TYPE[self._currentAction]

        umlFrame: UmlFrame = self._source.umlFrame

        command: CommandCreateUmlLink = CommandCreateUmlLink(umlFrame=umlFrame,
                                                             appPubSubEngine=self._appPubSubEngine,
                                                             umlPubSubEngine=self._umlPubSubEngine,
                                                             source=self._source,
                                                             destination=self._destination,
                                                             linkType=linkType
                                                             )
        return command

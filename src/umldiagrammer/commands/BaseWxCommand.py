
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Command


from pyutmodelv2.PyutLinkedObject import PyutLinkedObject

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlUseCase import UmlUseCase
from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

from umlshapes.types.Common import UmlShapeList
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umldiagrammer.commands.CommandTypes import DoableObjectType
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine


class BaseWxCommand(Command):

    def __init__(self, canUndo: bool, name: str,  appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            canUndo:
            name:
            appPubSubEngine:
            umlPubSubEngine:
        """
        super().__init__(canUndo=canUndo, name=name)

        self._baseLogger:      Logger           = getLogger(__name__)
        self._name:            str              = name
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        self._umlPreferences:  UmlPreferences        = UmlPreferences()
        self._appPreferences:  DiagrammerPreferences = DiagrammerPreferences()

    def _addUmClassToFrame(self, umlClass: UmlClass, umlFrame: UmlFrame, umlPosition: UmlPosition):

        umlClass.umlFrame = umlFrame
        umlClass.position = umlPosition

        diagram: UmlDiagram = umlFrame.umlDiagram

        diagram.AddShape(umlClass)
        umlClass.Show(True)

        eventHandler: UmlClassEventHandler = UmlClassEventHandler()
        eventHandler.SetShape(umlClass)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlClass.GetEventHandler())
        umlClass.SetEventHandler(eventHandler)

        umlFrame.refresh()

        if self._appPreferences.autoResizeShapesOnEdit is True:
            umlClass.autoSize()

        self._baseLogger.info(f'Created {umlClass}')

    def _removeUmlShapeFromFrame(self, umlFrame: UmlFrame, umlShape: DoableObjectType, pyutClass: PyutLinkedObject | None = None):

        umlShapes: UmlShapeList = umlFrame.umlShapes

        for obj in umlShapes:

            # This is a duplicate of the UmlObject, since I cannot use NewType
            # if isinstance(obj, (OglClass, OglLink, OglNote, OglText, OglSDMessage, OglSDInstance, OglActor, OglUseCase, OglInterface2)):

            potentialObject: UmlClass = cast(UmlClass, obj)

            if self._isSameShape(objectToRemove=umlShape, potentialObject=potentialObject):

                umlDiagram:       UmlDiagram       = umlFrame.umlDiagram
                pyutLinkedObject: PyutLinkedObject = self._getPyutLinkedObject(umlShape=potentialObject)

                if pyutClass in pyutLinkedObject.parents:
                    self._baseLogger.warning(f'Removing {pyutClass=} from {pyutLinkedObject=}')
                    for parent in pyutLinkedObject.parents:
                        umlDiagram.RemoveShape(parent)

                umlDiagram.RemoveShape(potentialObject)
                self._baseLogger.info(f'{potentialObject} deleted')
                umlFrame.refresh()

    def _isSameShape(self, objectToRemove: DoableObjectType, potentialObject: DoableObjectType) -> bool:
        """
        This probably could be done by updating the UML Shapes with the __equ__ dunder method.
        Wait until the umlshapes project updates

        Args:
            objectToRemove:   Object we were told to remove
            potentialObject:  The one that is on the frame

        Returns:  `True` if they are one and the same, else `False`

        """
        ans: bool = False

        # if isinstance(objectToRemove, UmlSDInstance):
        #     nonOglObject: OglSDInstance = cast(OglSDInstance, objectToRemove)
        #     if nonOglObject.pyutSDInstance.id == nonOglObject.pyutSDInstance.id:
        #         ans = True
        # else:
        if objectToRemove.id == potentialObject.id:
            ans = True

        return ans

    def _getPyutLinkedObject(self, umlShape: UmlActor | UmlClass | UmlNote | UmlUseCase) -> PyutLinkedObject:

        if isinstance(umlShape, UmlActor) is True:
            umlActor: UmlActor = cast(UmlActor, umlShape)
            return umlActor.pyutActor
        elif isinstance(umlShape, UmlClass) is True:
            umlClass: UmlClass = cast(UmlClass, umlShape)
            return umlClass.pyutClass
        elif isinstance(umlShape, UmlNote) is True:
            umlNote: UmlNote = cast(UmlNote, umlShape)
            return umlNote.pyutNote
        else:
            umlUseCase: UmlUseCase = cast(UmlUseCase, umlShape)
            return umlUseCase.pyutUseCase

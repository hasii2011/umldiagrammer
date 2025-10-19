
from logging import Logger
from logging import getLogger

from wx import OK
from wx import Command

from pyutmodelv2.PyutModelTypes import ClassName
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces

from umlshapes.UmlUtils import UmlUtils

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.dialogs.DlgEditInterface import DlgEditInterface

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

from umlshapes.types.Common import AttachmentSide
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.links.eventhandlers.UmlLollipopInterfaceEventHandler import UmlLollipopInterfaceEventHandler

from umldiagrammer.data.LollipopCreationData import LollipopCreationData

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

class CommandCreateLollipopInterface(Command):
    pyutInterfaceCount: int = 0

    def __init__(self, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine, creationData: LollipopCreationData):
        """

        Args:
            appPubSubEngine:
            umlPubSubEngine:
            creationData:
        """

        name: str = f'Lollipop{CommandCreateLollipopInterface.pyutInterfaceCount}'
        super().__init__(canUndo=True, name=name)

        self.logger:           Logger = getLogger(__name__)
        self._name:            str              = name
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        self._creationData: LollipopCreationData = creationData

        self._umlPreferences:    UmlPreferences = UmlPreferences()
        self._prototypeLollipop: UmlLollipopInterface  = self._createLollipopInterface()

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True

    def Do(self) -> bool:
        requestingFrame: ClassDiagramFrame = self._creationData.requestingFrame
        pyutInterfaces:  PyutInterfaces    = self._creationData.pyutInterfaces

        with DlgEditInterface(parent=requestingFrame,
                              lollipopInterface=self._prototypeLollipop,
                              umlPubSubEngine=self._umlPubSubEngine,
                              pyutInterfaces=pyutInterfaces) as dlg:
            if dlg.ShowModal() == OK:
                diagram: UmlDiagram = requestingFrame.umlDiagram  # And then I break the opaqueness

                diagram.AddShape(self._prototypeLollipop)
                self._prototypeLollipop.Show(show=True)
                self.logger.info(f'UmlInterface added: {self._prototypeLollipop}')

                requestingFrame.refresh()
                return True
            else:
                return False

    def Undo(self) -> bool:
        self.logger.info(f'Undo create {self._prototypeLollipop}')
        self._creationData.requestingFrame.umlDiagram.RemoveShape(self._prototypeLollipop)
        self._creationData.requestingFrame.refresh()

        return True

    def _createLollipopInterface(self) -> UmlLollipopInterface:
        """
        """
        creationData:       LollipopCreationData = self._creationData
        requestingFrame:    ClassDiagramFrame    = creationData.requestingFrame
        requestingUmlClass: UmlClass             = creationData.requestingUmlClass
        pyutInterfaces:     PyutInterfaces       = creationData.pyutInterfaces
        perimeterPoint:     UmlPosition          = creationData.perimeterPoint

        interfaceName: str = f'{self._umlPreferences.defaultNameInterface}{CommandCreateLollipopInterface.pyutInterfaceCount}'
        CommandCreateLollipopInterface.pyutInterfaceCount += 1

        pyutInterface: PyutInterface = PyutInterface(interfaceName)
        pyutInterface.addImplementor(ClassName(requestingUmlClass.pyutClass.name))

        umlLollipopInterface: UmlLollipopInterface = UmlLollipopInterface(pyutInterface=pyutInterface)
        umlLollipopInterface.attachedTo            = requestingUmlClass

        attachmentSide: AttachmentSide      = UmlUtils.attachmentSide(x=perimeterPoint.x, y=perimeterPoint.y, rectangle=requestingUmlClass.rectangle)
        umlLollipopInterface.attachmentSide = attachmentSide
        umlLollipopInterface.lineCentum     = UmlUtils.computeLineCentum(attachmentSide=attachmentSide, umlPosition=perimeterPoint, rectangle=requestingUmlClass.rectangle)

        self.logger.debug(f'{umlLollipopInterface.attachmentSide=} {umlLollipopInterface.lineCentum=}')

        umlLollipopInterface.umlFrame = requestingFrame

        eventHandler: UmlLollipopInterfaceEventHandler = UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)
        eventHandler.SetPreviousHandler(umlLollipopInterface.GetEventHandler())
        umlLollipopInterface.SetEventHandler(eventHandler)

        # Update with our generated one
        pyutInterfaces.append(pyutInterface)

        return umlLollipopInterface

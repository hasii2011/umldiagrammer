
from typing import Dict
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from enum import Enum

from wx import Bitmap
from wx import BitmapBundle

from wx.lib.embeddedimage import PyEmbeddedImage

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences
from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize

NO_BITMAP: Bitmap = cast(Bitmap, None)

class IconName(Enum):
    ACTOR       = 'Actor'
    CLASS       = 'Class'
    TEXT        = 'Text'
    USECASE     = 'UseCase'
    NOTE        = 'Note'
    UNDO        = 'Undo'
    REDO        = 'Redo'
    POINTER     = 'Pointer'

    AGGREGATION = 'Aggregation'
    ASSOCIATION = 'Association'
    COMPOSITION = 'Composition'
    INHERITANCE = 'Inheritance'
    REALIZATION = 'Realization'
    NOTE_ASSOCIATION = 'NoteAssociation'

    NEW_PROJECT  = 'NewProject'
    OPEN_PROJECT = 'OpenProject'
    SAVE_PROJECT = 'SaveProject'

    NEW_CLASS_DIAGRAM    = 'NewClassDiagram'
    NEW_SEQUENCE_DIAGRAM = 'NewSequenceDiagram'
    NEW_USECASE_DIAGRAM  = 'NewUseCaseDiagram'

    SEQUENCE_DIAGRAM_INSTANCE = 'SequenceDiagramInstance'
    SEQUENCE_DIAGRAM_MESSAGE  = 'SequenceDiagramMessage'


IconMap = NewType('IconMap', Dict[IconName, BitmapBundle])


class ToolBarIcons:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        diagrammerPreferences: DiagrammerPreferences = DiagrammerPreferences()

        self._iconMap: IconMap = IconMap({})

        if diagrammerPreferences.toolBarIconSize == ToolBarIconSize.SMALL:
            self._loadSmallIcons()
            self.logger.debug(f'Loaded the small icons')
        elif diagrammerPreferences.toolBarIconSize == ToolBarIconSize.MEDIUM:
            self._loadMediumIcons()
            self.logger.debug(f'Loaded the medium icons')
        elif diagrammerPreferences.toolBarIconSize == ToolBarIconSize.LARGE:
            self._loadLargeIcons()
            self.logger.debug(f'Loaded the large icons')
        elif diagrammerPreferences.toolBarIconSize == ToolBarIconSize.EXTRA_LARGE:
            self._loadExtraLargeIcons()
            self.logger.debug(f'Loaded the extra large icons')

    def getIcon(self, iconName: IconName) -> BitmapBundle:
        return BitmapBundle(self._iconMap[iconName])

    def _loadSmallIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded16

        for variableName in dir(codeallyadvanced.resources.umldiagrammer.Embedded16):
            if not variableName.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded16, variableName)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp: Bitmap = pyEmbeddedImage.GetBitmap()
                    self._iconMap[IconName(variableName)] = bmp

    def _loadLargeIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded32

        for variableName in dir(codeallyadvanced.resources.umldiagrammer.Embedded32):
            if not variableName.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded32, variableName)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp: Bitmap = pyEmbeddedImage.GetBitmap()
                    self._iconMap[IconName(variableName)] = bmp

    def _loadMediumIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded24

        for variableName in dir(codeallyadvanced.resources.umldiagrammer.Embedded24):
            if not variableName.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded24, variableName)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp: Bitmap = pyEmbeddedImage.GetBitmap()
                    self._iconMap[IconName(variableName)] = bmp

    def _loadExtraLargeIcons(self):

        import codeallyadvanced.resources.umldiagrammer.Embedded64

        for variableName in dir(codeallyadvanced.resources.umldiagrammer.Embedded64):
            if not variableName.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded64, variableName)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp: Bitmap = pyEmbeddedImage.GetBitmap()
                    self._iconMap[IconName(variableName)] = bmp

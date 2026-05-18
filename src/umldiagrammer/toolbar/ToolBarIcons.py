
from typing import Dict
from typing import cast
from typing import NewType

from types import ModuleType

from logging import Logger
from logging import getLogger

from importlib import import_module

from enum import StrEnum

from wx import Bitmap
from wx import BitmapBundle

from wx.lib.embeddedimage import PyEmbeddedImage

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.toolbar.ToolBarTheme import ToolBarTheme
from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize

NO_BITMAP: Bitmap = cast(Bitmap, None)

class IconName(StrEnum):
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

    DEFAULT_PREFERENCES = 'DefaultPreferences'          # Not a toolbar icon but
    LOLLIPOP            = 'Lollipop'                    # in the Embbeded module

    SEQUENCE_DIAGRAM_INSTANCE = 'SequenceDiagramInstance'
    SEQUENCE_DIAGRAM_MESSAGE  = 'SequenceDiagramMessage'


IconMap = NewType('IconMap', Dict[IconName, BitmapBundle])

MODULE_NAME_EXTRA_LARGE: str = 'Embedded64'
MODULE_NAME_LARGE:       str = 'Embedded32'
MODULE_NAME_MEDIUM:      str = 'Embedded24'
MODULE_NAME_SMALL:       str = 'Embedded16'


class NoSuchModuleException(Exception):
    pass

class ToolBarIcons:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        diagrammerPreferences: DiagrammerPreferences = DiagrammerPreferences()
        self._iconMap:         IconMap               = IconMap({})
        toolbarTheme:          ToolBarTheme          = diagrammerPreferences.toolbarTheme
        toolBarIconSize:       ToolBarIconSize       = diagrammerPreferences.toolBarIconSize

        mapSizeToPackage:      Dict[ToolBarIconSize, str] = {
            ToolBarIconSize.EXTRA_LARGE: MODULE_NAME_EXTRA_LARGE,
            ToolBarIconSize.LARGE:       MODULE_NAME_LARGE,
            ToolBarIconSize.MEDIUM:      MODULE_NAME_MEDIUM,
            ToolBarIconSize.SMALL:       MODULE_NAME_SMALL
        }
        embeddedPackageName: str = mapSizeToPackage[toolBarIconSize]

        self._loadIcons(
            imagePackage=toolbarTheme.value,
            embeddedPackageName=embeddedPackageName
        )

    def getIcon(self, iconName: IconName) -> BitmapBundle:
        return BitmapBundle(self._iconMap[iconName])

    def _loadIcons(self, imagePackage: str, embeddedPackageName: str):
        """

        Args:
            imagePackage:           Specifies the theme
            embeddedPackageName:    Specifies the size

        """

        moduleObj: ModuleType = self._importModule(imagePackage=imagePackage, embeddedPackageName=embeddedPackageName)

        for variableName in dir(moduleObj):
            if not variableName.startswith("__"):
                # self.logger.info(f'{embedded=}')
                pyEmbeddedImage: PyEmbeddedImage = getattr(moduleObj, variableName)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp: Bitmap = pyEmbeddedImage.GetBitmap()
                    self._iconMap[IconName(variableName)] = bmp

    def _importModule(self, imagePackage: str, embeddedPackageName: str) -> ModuleType:

        moduleStr: str = f'{imagePackage}.{embeddedPackageName}'
        try:
            moduleObj: ModuleType = import_module(moduleStr)
        except ImportError:
            self.logger.error(f'Failed to import icon package: {moduleStr}')
            raise NoSuchModuleException(f'Failed to import icon package: {moduleStr}')

        return moduleObj

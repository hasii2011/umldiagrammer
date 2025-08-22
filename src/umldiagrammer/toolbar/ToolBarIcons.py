
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Bitmap

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences
from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize

NO_BITMAP: Bitmap = cast(Bitmap, None)


class ToolBarIcons:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._newProjectIcon:          Bitmap = NO_BITMAP
        self._newClassDiagramIcon:     Bitmap = NO_BITMAP
        self._newSequenceDiagramIcon:  Bitmap = NO_BITMAP
        self._newUseCaseDiagramIcon:   Bitmap = NO_BITMAP

        diagrammerPreferences: DiagrammerPreferences = DiagrammerPreferences()

        if diagrammerPreferences.toolBarIconSize == ToolBarIconSize.SMALL:
            self._loadSmallIcons()
        elif diagrammerPreferences.toolBarIconSize == ToolBarIconSize.MEDIUM:
            self._loadMediumIcons()
        elif diagrammerPreferences.toolBarIconSize == ToolBarIconSize.LARGE:
            self._loadLargeIcons()

    @property
    def iconNewProject(self) -> Bitmap:
        return self._newProjectIcon

    @property
    def iconNewClassDiagram(self) -> Bitmap:
        return self._newClassDiagramIcon

    @property
    def iconNewSequenceDiagramIcon(self) -> Bitmap:
        return self._newSequenceDiagramIcon

    @property
    def iconNewUseCaseDiagramIcon(self) -> Bitmap:
        return self._newUseCaseDiagramIcon

    def _loadSmallIcons(self):
        self._loadSmallMenuToolIcons()

    def _loadSmallMenuToolIcons(self):
        from codeallyadvanced.resources.umldiagrammer.Embedded16 import NewProject
        from codeallyadvanced.resources.umldiagrammer.Embedded16 import NewClassDiagram
        from codeallyadvanced.resources.umldiagrammer.Embedded16 import NewSequenceDiagram
        from codeallyadvanced.resources.umldiagrammer.Embedded16 import NewUseCaseDiagram

        self._newProjectIcon         = NewProject.GetBitmap()
        self._newClassDiagramIcon    = NewClassDiagram.GetBitmap()
        self._newSequenceDiagramIcon = NewSequenceDiagram.GetBitmap()
        self._newUseCaseDiagramIcon  = NewUseCaseDiagram.GetBitmap()

    def _loadMediumIcons(self):
        from codeallyadvanced.resources.umldiagrammer.Embedded24 import NewProject
        from codeallyadvanced.resources.umldiagrammer.Embedded24 import NewClassDiagram
        from codeallyadvanced.resources.umldiagrammer.Embedded24 import NewSequenceDiagram
        from codeallyadvanced.resources.umldiagrammer.Embedded24 import NewUseCaseDiagram

        self._newProjectIcon      = NewProject.GetBitmap()
        self._newClassDiagramIcon = NewClassDiagram.GetBitmap()
        self._newSequenceDiagramIcon = NewSequenceDiagram.GetBitmap()
        self._newUseCaseDiagramIcon  = NewUseCaseDiagram.GetBitmap()

    def _loadLargeIcons(self):
        from codeallyadvanced.resources.umldiagrammer.Embedded32 import NewProject
        from codeallyadvanced.resources.umldiagrammer.Embedded32 import NewClassDiagram
        self._newProjectIcon      = NewProject.GetBitmap()
        self._newClassDiagramIcon = NewClassDiagram.GetBitmap()

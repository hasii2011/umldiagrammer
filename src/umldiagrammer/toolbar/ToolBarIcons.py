
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

        self._newProjectIcon:         Bitmap = NO_BITMAP

        diagrammerPreferences: DiagrammerPreferences = DiagrammerPreferences()

        if diagrammerPreferences.toolBarIconSize == ToolBarIconSize.SIZE_16:
            self._loadSmallIcons()
        elif diagrammerPreferences.toolBarIconSize == ToolBarIconSize.SIZE_32:
            self._loadLargeIcons()

    @property
    def iconNewProject(self):
        return self._newProjectIcon

    def _loadSmallIcons(self):
        self._loadSmallMenuToolIcons()

    def _loadSmallMenuToolIcons(self):

        # from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxNewProject import embeddedImage as ImgToolboxNewProject
        from umldiagrammer.resources.icons.embedded32.NewProject import embeddedImage as ImgToolboxNewProject
        self._newProjectIcon = ImgToolboxNewProject.GetBitmap()

    def _loadLargeIcons(self):
        from umldiagrammer.resources.icons.embedded32.NewProject import embeddedImage as ImgToolboxNewProject
        self._newProjectIcon = ImgToolboxNewProject.GetBitmap()

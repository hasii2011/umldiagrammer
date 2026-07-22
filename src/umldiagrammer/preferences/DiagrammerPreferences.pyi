from pathlib import Path

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from umldiagrammer.preferences.ProjectHistoryDisplayType import ProjectHistoryDisplayType
from umldiagrammer.preferences.ProjectTabPosition import ProjectTabPosition
from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize
from umldiagrammer.toolbar.ToolBarPosition import ToolBarPosition
from umldiagrammer.toolbar.ToolBarTheme import ToolBarTheme


class DiagrammerPreferences:
    loadLastOpenedProject: bool
    autoResizeShapesOnEdit: bool
    diagramsDirectory: Path
    toolBarIconSize: ToolBarIconSize
    toolbarTheme: ToolBarTheme
    fileHistoryDisplay: ProjectHistoryDisplayType
    saveOnlyWritesCompressed: bool
    displayProjectExtension: bool
    fullScreen: bool
    startupSize: Dimensions
    centerAppOnStartup: bool
    startupPosition: Position
    toolBarPosition: ToolBarPosition
    projectTabPosition: ProjectTabPosition
    inTestMode: bool
    testPosition: Position
    testSize: Dimensions

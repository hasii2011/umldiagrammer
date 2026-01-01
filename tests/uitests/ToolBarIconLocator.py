
from typing import cast

from functools import cached_property

from pathlib import Path

from dataclasses import dataclass

from pyautogui import Point
from pyautogui import locateCenterOnScreen

from codeallybasic.ResourceManager import ResourceManager


@dataclass
class Location:
    x: int = 0
    y: int = 0


LOCATION_NOT_SET:  Location = cast(Location, None)
LOCATE_CONFIDENCE: float    = 0.9

# noinspection SpellCheckingInspection
PACKAGE_NAME:  str = 'tests.uitests.resources.toolbaricons'
# noinspection SpellCheckingInspection
RESOURCE_PATH: str = 'tests/uitests/resources/toolbaricons'

class ToolBarIconLocator:
    """
    TODO:   Create a decorator that detects the empty cache and fills it
    """
    def __init__(self, confidence: float = LOCATE_CONFIDENCE):
        """

        Args:
            confidence:  The confidence level for the look ups
        """
        self._confidence: float = confidence

        self._resourcePath: Path = ResourceManager.computeResourcePath(resourcePath=RESOURCE_PATH, packageName=PACKAGE_NAME)

    @cached_property
    def aggregationLink(self) -> Location:
        return self._locate(bareFileName='AggregationLink.png')

    @cached_property
    def associationLink(self) -> Location:
        return self._locate(bareFileName='AssociationLink.png')

    @cached_property
    def compositionLink(self) -> Location:
        return self._locate(bareFileName='CompositionLink.png')

    @cached_property
    def inheritanceLink(self) -> Location:
        return self._locate(bareFileName='InheritanceLink.png')

    @cached_property
    def interfaceLink(self) -> Location:
        return self._locate(bareFileName='InterfaceLink.png')

    @cached_property
    def newActor(self) -> Location:
        return self._locate(bareFileName='NewActor.png')

    @cached_property
    def newClass(self) -> Location:
        return self._locate(bareFileName='NewClass.png')

    @cached_property
    def newClassDiagram(self) -> Location:
        return self._locate(bareFileName='NewClassDiagram.png')

    @cached_property
    def newNote(self) -> Location:
        return self._locate(bareFileName='NewNote.png')

    @cached_property
    def newText(self) -> Location:
        return self._locate(bareFileName='NewText.png')

    @cached_property
    def newUseCase(self) -> Location:
        return self._locate(bareFileName='NewUseCase.png')

    @cached_property
    def newUseCaseDiagram(self) -> Location:
        return self._locate(bareFileName='NewUseCaseDiagram.png')

    @cached_property
    def noteLink(self) -> Location:
        return self._locate(bareFileName='NoteLink.png')

    @cached_property
    def saveProject(self) -> Location:
        return self._locate(bareFileName='SaveProject.png')

    def _locate(self, bareFileName: str) -> Location:
        """
        Finds the image location on the screen
        Args:
            bareFileName:   The file name of the image

        Returns:  The location on the screen where that image is
        """

        path: Path  = self._resourcePath / bareFileName
        pt:   Point = locateCenterOnScreen(str(path), confidence=self._confidence)

        return Location(x=pt.x, y=pt.y)

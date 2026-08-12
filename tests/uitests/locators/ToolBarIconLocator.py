
from logging import Logger
from logging import getLogger

from codeallybasic.ResourceManager import ResourceManager

from tests.uitests.locators.BaseLocator import Location
from tests.uitests.locators.BaseLocator import BaseLocator
from tests.uitests.locators.BaseLocator import LOCATE_CONFIDENCE

# noinspection SpellCheckingInspection
PACKAGE_NAME:  str = 'tests.uitests.resources.toolbaricons'
# noinspection SpellCheckingInspection
RESOURCE_PATH: str = 'tests/uitests/resources/toolbaricons'

class ToolBarIconLocator(BaseLocator):
    """
    Locates toolbar icon images on screen.
    """
    def __init__(self, confidence: float = LOCATE_CONFIDENCE):
        """

        Args:
            confidence:  The confidence level for the look ups
        """
        resourcePath = ResourceManager.computeResourcePath(resourcePath=RESOURCE_PATH, packageName=PACKAGE_NAME)

        super().__init__(confidence=confidence, resourcePath=resourcePath)
        self.logger: Logger = getLogger(__name__)

        self.logger.info(f'Location Confidence: {self._confidence}')

    @property
    def aggregationLink(self) -> Location:
        return self._locate(bareFileName='AggregationLink.png')

    @property
    def associationLink(self) -> Location:
        return self._locate(bareFileName='AssociationLink.png')

    @property
    def compositionLink(self) -> Location:
        return self._locate(bareFileName='CompositionLink.png')

    @property
    def inheritanceLink(self) -> Location:
        return self._locate(bareFileName='InheritanceLink.png')

    @property
    def interfaceLink(self) -> Location:
        return self._locate(bareFileName='InterfaceLink.png')

    @property
    def newActor(self) -> Location:
        return self._locate(bareFileName='NewActor.png')

    @property
    def newClass(self) -> Location:
        return self._locate(bareFileName='NewClass.png')

    @property
    def newClassDiagram(self) -> Location:
        return self._locate(bareFileName='NewClassDiagram.png')

    @property
    def newNote(self) -> Location:
        return self._locate(bareFileName='NewNote.png')

    @property
    def newText(self) -> Location:
        return self._locate(bareFileName='NewText.png')

    @property
    def newUseCase(self) -> Location:
        return self._locate(bareFileName='NewUseCase.png')

    @property
    def newUseCaseDiagram(self) -> Location:
        return self._locate(bareFileName='NewUseCaseDiagram.png')

    @property
    def noteLink(self) -> Location:
        return self._locate(bareFileName='NoteLink.png')

    @property
    def saveProject(self) -> Location:
        return self._locate(bareFileName='SaveProject.png')

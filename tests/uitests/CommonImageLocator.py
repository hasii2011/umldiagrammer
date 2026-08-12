
from logging import Logger
from logging import getLogger

from codeallybasic.ResourceManager import ResourceManager

from tests.uitests.BaseLocator import BaseLocator

from tests.uitests.BaseLocator import Location

# noinspection SpellCheckingInspection
PACKAGE_NAME:  str = 'tests.uitests.resources.common'
# noinspection SpellCheckingInspection
RESOURCE_PATH: str = 'tests/uitests/resources/common'

COMMON_CONFIDENCE: float = 0.90


class CommonImageLocator(BaseLocator):
    """
    Locates common images on screen.
    """
    def __init__(self, confidence: float = COMMON_CONFIDENCE):
        """

        Args:
            confidence:  The confidence level for the look ups
        """
        resourcePath = ResourceManager.computeResourcePath(resourcePath=RESOURCE_PATH, packageName=PACKAGE_NAME)

        super().__init__(confidence=confidence, resourcePath=resourcePath)
        self.logger: Logger = getLogger(__name__)

        self.logger.info(f'Location Confidence: {self._confidence}')

    @property
    def saveAsProjectNameTextInput(self) -> Location:
        return self._locate('SaveAsProjectNameTextInput.png')

    @property
    def saveProjectAsButton(self) -> Location:
        return self._locate('SaveProjectAsButton.png')

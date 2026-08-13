
from logging import Logger
from logging import getLogger

from codeallybasic.ResourceManager import ResourceManager

from tests.uitests.locators.BaseLocator import BaseLocator
from tests.uitests.locators.BaseLocator import Location

CLASS_LOCATOR_CONFIDENCE: float = 0.90


PACKAGE_NAME:  str = 'tests.uitests.resources.umlclasslocator'
RESOURCE_PATH: str = 'tests/uitests/resources/umlclasslocator'


class UmlClassLocator(BaseLocator):

    def __init__(self, confidence: float = CLASS_LOCATOR_CONFIDENCE):
        """

        Args:
            confidence:  The confidence level for the look ups
        """
        resourcePath = ResourceManager.computeResourcePath(resourcePath=RESOURCE_PATH, packageName=PACKAGE_NAME)

        super().__init__(confidence=confidence, resourcePath=resourcePath)
        self.logger: Logger = getLogger(__name__)

        self.logger.info(f'Location Confidence: {self._confidence}')

    @property
    def aggregator(self) -> Location:
        return self._locate('Aggregator.png')

    @property
    def aggregated(self) -> Location:
        return self._locate('Aggregated.png')

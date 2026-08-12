
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from pathlib import Path

# noinspection PyPackageRequirements
from pyscreeze import Point
from pyautogui import locateCenterOnScreen
from pyautogui import ImageNotFoundException

@dataclass
class Location:
    x: int = 0
    y: int = 0


LOCATION_NOT_SET:  Location = cast(Location, None)

LOCATE_CONFIDENCE: float    = 0.95

class BaseLocator:
    def __init__(self, confidence: float, resourcePath: Path):

        self.baseLogger: Logger = getLogger(__name__)

        self._confidence:   float = confidence
        self._resourcePath: Path  = resourcePath

    def _locate(self, bareFileName: str) -> Location:
        """
        Finds the image location on the screen
        Args:
            bareFileName:   The file name of the image

        Returns:  The location on the screen where that image is
        """

        try:
            path:        Path         = self._resourcePath / bareFileName
            targetPoint: Point | None = locateCenterOnScreen(
                str(path),
                confidence=self._confidence,
                grayscale=True
            )

            if targetPoint is not None:
                # Divide by 2 on macOS Retina displays to convert physical pixels to logical points
                logicalX: int = int(targetPoint.x / 2)
                logicalY: int = int(targetPoint.y / 2)
                return Location(x=logicalX, y=logicalY)
        except ImageNotFoundException:
            self.baseLogger.error(f'Where the heck is the image for {bareFileName}')

        return LOCATION_NOT_SET

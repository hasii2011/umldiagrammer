
from logging import Logger
from logging import getLogger

from pyautogui import click

from tests.uitests.locators.BaseLocator import Location
from tests.uitests.locators.ToolBarIconLocator import ToolBarIconLocator


class ToolBarClicker:

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._iconLocator: ToolBarIconLocator = ToolBarIconLocator()

    def clickNewClass(self):
        location: Location = self._iconLocator.newClass
        click(x=location.x,   y=location.y)

    def clickAggregation(self):
        """
        Click on the Aggregation Link Icon
        """
        location: Location = self._iconLocator.aggregationLink
        click(x=location.x, y=location.y)

    def clickComposition(self):
        location: Location = self._iconLocator.compositionLink
        click(x=location.x, y=location.y)

    def clickInheritance(self):
        location: Location = self._iconLocator.inheritanceLink
        click(x=location.x, y=location.y)

    def clickSaveProject(self):
        location: Location = self._iconLocator.saveProject
        click(x=location.x, y=location.y)

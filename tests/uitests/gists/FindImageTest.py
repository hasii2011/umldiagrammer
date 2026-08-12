#!/usr/bin/env python
# /// script
# dependencies = ['pillow', 'pyautogui', 'umlshapes', 'opencv-python']
# ///

from typing import Dict

import logging

from pyautogui import size
from pyautogui import ImageNotFoundException

from tests.uitests.ToolBarIconLocator import Location
from tests.uitests.ToolBarIconLocator import ToolBarIconLocator
from tests.uitests.Common import setupLogging

if __name__ == '__main__':
    setupLogging()
    logging.info(f'Remember.  The image size has to match')
    logging.info(f'Screen size{size()}')

    iconProperties: Dict[str, property] = {}
    for attributeName in dir(ToolBarIconLocator):
        potentialProperty = getattr(ToolBarIconLocator, attributeName)
        if isinstance(potentialProperty, property):
            iconProperties[attributeName] = potentialProperty

    logging.debug(f'The icon properties are: {iconProperties}')

    iconLocator: ToolBarIconLocator = ToolBarIconLocator()
    for propName in iconProperties.keys():
        try:
            targetLocation: Location = getattr(iconLocator, propName)
            logging.info(f'{propName} - ({targetLocation.x},{targetLocation.y})')
        except ImageNotFoundException:
            logging.error(f'Where the heck is the image for {propName}')

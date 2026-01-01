#!/usr/bin/env python
# /// script
# dependencies = ['pillow', 'pyautogui', 'umlshapes', 'opencv-python']
# ///

import logging
from logging import basicConfig
from logging import INFO
from typing import Dict

# from typing import reveal_type

from functools import cached_property

from pyautogui import ImageNotFoundException

from tests.uitests.ToolBarIconLocator import Location
from tests.uitests.ToolBarIconLocator import ToolBarIconLocator

BEST_FORMAT:   str = '%(asctime)s.%(msecs)03d %(levelname)-5s %(name)-4s - %(message)s'
SIMPLE_FORMAT: str = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s'
TEST_FORMAT:   str = '%(levelname)s: %(module)s: %(message)s'

def setupLogging():
    basicConfig(
        level=INFO,
        format=TEST_FORMAT
    )


if __name__ == '__main__':
    """
    How to get and store property references for later invocation was done with the 
    help of Gemini 0.22.5,  Gemini 1.5 Flash model
    
     1. To store the property object: Use ClassName.property_name.
     2. To invoke the stored property later: Use stored_property_object.__get__(instance).

    mypy does not seem to think the list contains properties
    I feel so dirty
    """

    setupLogging()
    logging.info(f'Remember.  The image size has to match')
    # eveal_type(ToolBarIconLocator.aggregationLink)

    #
    #  I find Python comprehensions, incomprehensible
    #
    cachedProperties: Dict[str, cached_property] = {}
    for attributeName in dir(ToolBarIconLocator):
        potentialProperty = getattr(ToolBarIconLocator, attributeName)
        if isinstance(potentialProperty, cached_property):
            cachedProperties[attributeName] = potentialProperty

    logging.debug(f"The cached properties are: {cachedProperties}")

    iconLocator: ToolBarIconLocator = ToolBarIconLocator()
    for propName, prop in cachedProperties.items():

        try:
            pt: Location = prop.__get__(iconLocator)
            logging.info(f'{propName} - ({pt.x},{pt.y})')
        except ImageNotFoundException:
            logging.error(f'Where the heck is the image for {propName}')

    cachedLocation: Location = ToolBarIconLocator.aggregationLink.__get__(iconLocator)
    logging.info(f'Cached Location: ({cachedLocation.x},{cachedLocation.y})')

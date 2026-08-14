#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes', 'opencv-python']
# ///
"""
From the command line and if you have `uv` installed
you can execute this script as follow:

uv run checkComposition.py
"""
from pathlib import Path

import pyautogui
from pyautogui import click
from pymsgbox import alert

from umlshapes.types.UmlPosition import UmlPosition

from tests.uitests.Common import PAUSE_AFTER_EACH_CALL
from tests.uitests.Common import createClassPair
from tests.uitests.Common import displayAppropriateDialog
from tests.uitests.Common import isAppRunning
from tests.uitests.Common import makeAppActive
from tests.uitests.Common import wasTestSuccessful

from tests.uitests.SaveAsProject import SaveAsProject

from tests.uitests.locators.BaseLocator import Location
from tests.uitests.locators.ToolBarIconLocator import ToolBarIconLocator
from tests.uitests.locators.UmlClassLocator import UmlClassLocator

#
# Removed the IDs;  Also, removed the ModelLink name
#
GOLDEN_COMPOSITION_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/compositiontest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="107" height="90" x="199" y="152">\n'
    '            <ModelClass id="" name="TheComposer" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlClass id="" width="82" height="90" x="549" y="447">\n'
    '            <ModelClass id="" name="Composed" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlLink id="" fromX="304" fromY="242" toX="549" toY="456" spline="False">\n'
    '            <AssociationName deltaX="0" deltaY="0" />\n'
    '            <SourceCardinality deltaX="0" deltaY="0" />\n'
    '            <DestinationCardinality deltaX="0" deltaY="30" />\n'
    '            <ModelLink name="" type="COMPOSITION" sourceId="" destinationId="" bidirectional="False" sourceCardinalityValue="src Card" destinationCardinalityValue="dst Card" />\n'
    '        </UmlLink>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)
BASENAME:                         str  = 'compositiontest'
COMPOSITION_XML_FILENAME:         str = f'{BASENAME}.xml'
COMPOSITION_FILENAME:             Path = Path(f'/tmp/{BASENAME}.udt')
DECOMPRESSED_COMPOSITION_PROJECT: Path = Path(f'/tmp/{COMPOSITION_XML_FILENAME}')

LOC_WHERE_COMPOSER_IS_CREATED: UmlPosition = UmlPosition(x=475, y=255)
LOC_WHERE_COMPOSED_IS_CREATED: UmlPosition = UmlPosition(x=825, y=550)


if __name__ == '__main__':
    pyautogui.PAUSE = PAUSE_AFTER_EACH_CALL
    pyautogui.FAILSAFE = True

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()
        COMPOSITION_FILENAME.unlink(missing_ok=True)
        DECOMPRESSED_COMPOSITION_PROJECT.unlink(missing_ok=True)

        iconLocator:     ToolBarIconLocator = ToolBarIconLocator()
        umlClassLocator: UmlClassLocator    = UmlClassLocator()

        createClassPair(
            class1Location=LOC_WHERE_COMPOSER_IS_CREATED,
            class1Name='TheComposer',
            class2Location=LOC_WHERE_COMPOSED_IS_CREATED,
            class2Name='Composed'
        )
        #
        # Click on the Composition Link Icon
        #
        newCompositionLinkLocation: Location = iconLocator.compositionLink
        click(x=newCompositionLinkLocation.x, y=newCompositionLinkLocation.y)

        composerLocation: Location = umlClassLocator.composer
        click(x=composerLocation.x, y=composerLocation.y)
        print(f'{composerLocation=}')

        composedLocation: Location = umlClassLocator.composed
        click(x=composedLocation.x, y=composedLocation.y)
        print(f'{composedLocation=}')

        saveAsProject: SaveAsProject = SaveAsProject()
        saveAsProject.execute(projectFileName=str(COMPOSITION_FILENAME))

        success: bool = wasTestSuccessful(
            projectFileName=COMPOSITION_FILENAME,
            decompressedProjectFileName=DECOMPRESSED_COMPOSITION_PROJECT,
            goldenXml=GOLDEN_COMPOSITION_XML
        )

        displayAppropriateDialog(status=success)

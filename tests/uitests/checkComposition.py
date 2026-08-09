#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes']
# ///
"""
From the command line and if you have `uv` installed
you can execute this script as follow:

uv run checkComposition.py
"""
from pathlib import Path

import pyautogui
from pyautogui import write
from pyautogui import press
from pyautogui import click
from pymsgbox import alert

from tests.uitests.common import BACKSPACES_CLEAR_CLASS_NAME
from tests.uitests.common import LOC_TOOLBAR_Y
from tests.uitests.common import PAUSE_AFTER_EACH_CALL
from tests.uitests.common import displayAppropriateDialog
from tests.uitests.common import invokeSaveAsProject
from tests.uitests.common import isAppRunning
from tests.uitests.common import makeAppActive
from tests.uitests.common import wasTestSuccessful

#
# Removed the IDs;  Also, removed the ModelLink name
#
GOLDEN_COMPOSITION_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/CompositionTest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="78" height="90" x="539" y="242">\n'
    '            <ModelClass id="" name="Composer" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlClass id="" width="82" height="90" x="764" y="502">\n'
    '            <ModelClass id="" name="Composed" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlLink id="" fromX="617" fromY="332" toX="766" toY="502" spline="False">\n'
    '            <AssociationName deltaX="0" deltaY="0" />\n'
    '            <SourceCardinality deltaX="0" deltaY="0" />\n'
    '            <DestinationCardinality deltaX="0" deltaY="30" />\n'
    '            <ModelLink name="" type="COMPOSITION" sourceId="" destinationId="" bidirectional="False" sourceCardinalityValue="src Card" destinationCardinalityValue="dst Card" />\n'
    '        </UmlLink>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)
BASENAME:                         str  = 'CompositionTest'
COMPOSITION_XML_FILENAME:         str = f'{BASENAME}.xml'
COMPOSITION_FILENAME:             Path = Path(f'/tmp/{BASENAME}.udt')
DECOMPRESSED_COMPOSITION_PROJECT: Path = Path(f'/tmp/{COMPOSITION_XML_FILENAME}')

COMPOSITION_FILENAME.unlink(missing_ok=True)
DECOMPRESSED_COMPOSITION_PROJECT.unlink(missing_ok=True)

if __name__ == '__main__':
    pyautogui.PAUSE = PAUSE_AFTER_EACH_CALL
    pyautogui.FAILSAFE = True

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        click(x=730, y=LOC_TOOLBAR_Y)       # Click Create New class
        click(x=775, y=365)                 # Click in class name
        # click(x=473, y=331)
        # click(x=826, y=366)
        press('backspace', presses=BACKSPACES_CLEAR_CLASS_NAME)
        write('Composer')
        click(x=935, y=690)                 # Cick Ok button
        click(x=730, y=LOC_TOOLBAR_Y)       # Click Create New class

        click(x=1000, y=625)
        click(x=775, y=365)                 # Click in class name
        press('backspace', presses=BACKSPACES_CLEAR_CLASS_NAME)
        write('Composed')
        click(x=935, y=690)                 # Cick Ok button

        click(x=1020, y=LOC_TOOLBAR_Y)      # Click Composition
        click(x=810, y=390)                 # Click on Composer
        click(x=1040, y=650)                # Click on Composed
        #
        invokeSaveAsProject(projectFileName=str(COMPOSITION_FILENAME))
        #
        success: bool = wasTestSuccessful(
            projectFileName=COMPOSITION_FILENAME,
            decompressedProjectFileName=DECOMPRESSED_COMPOSITION_PROJECT,
            goldenXml=GOLDEN_COMPOSITION_XML
        )

        displayAppropriateDialog(status=success)

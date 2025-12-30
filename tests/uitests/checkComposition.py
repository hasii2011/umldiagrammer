#!/usr/bin/env python
# /// script
# dependencies = ["pyautogui"]
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
    '        <UmlClass id="" width="78" height="90" x="213" y="232">\n'
    '            <ModelClass id="" name="Composer" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlClass id="" width="82" height="90" x="620" y="401">\n'
    '            <ModelClass id="" name="Composed" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlLink id="" fromX="291" fromY="293" toX="620" toY="429" spline="False">\n'
    '            <AssociationName deltaX="0" deltaY="0" />\n'
    '            <SourceCardinality deltaX="0" deltaY="0" />\n'
    '            <DestinationCardinality deltaX="0" deltaY="0" />\n'
    '            <ModelLink name="" type="COMPOSITION" sourceId="" destinationId="" bidirectional="False" sourceCardinalityValue="" destinationCardinalityValue="" />\n'
    '        </UmlLink>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)
BASENAME:                         str  = 'CompositionTest'
COMPOSITION_XML_FILENAME:         str = f'{BASENAME}.xml'
COMPOSITION_FILENAME:             Path = Path(f'/tmp/{BASENAME}.udt')
DECOMPRESSED_COMPOSITION_PROJECT: Path = Path(f'/tmp/{COMPOSITION_XML_FILENAME}')

pyautogui.PAUSE = 0.5

COMPOSITION_FILENAME.unlink(missing_ok=True)
DECOMPRESSED_COMPOSITION_PROJECT.unlink(missing_ok=True)

if __name__ == '__main__':

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        click(x=770, y=323)
        click(x=729, y=70)
        click(x=473, y=331)
        click(x=826, y=366)
        press('backspace', presses=13)
        write('Composer')
        click(x=985, y=696)
        click(x=728, y=66)
        click(x=880, y=500)
        click(x=782, y=364)
        press('backspace', presses=12)
        write('Composed')
        click(x=982, y=681)
        click(x=1022, y=72)
        click(x=510, y=371)
        click(x=911, y=543)

        invokeSaveAsProject(projectFileName=str(COMPOSITION_FILENAME))

        success: bool = wasTestSuccessful(
            projectFileName=COMPOSITION_FILENAME,
            decompressedProjectFileName=DECOMPRESSED_COMPOSITION_PROJECT,
            goldenXml=GOLDEN_COMPOSITION_XML
        )

        displayAppropriateDialog(status=success)

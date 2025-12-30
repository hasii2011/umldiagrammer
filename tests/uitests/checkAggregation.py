#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes']
# ///
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
GOLDEN_AGGREGATION_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/AggregationTest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="84" height="90" x="73" y="165">\n'
    '            <ModelClass id="" name="Aggregator" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlClass id="" width="88" height="90" x="688" y="395">\n'
    '            <ModelClass id="" name="Aggregated" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlLink id="" fromX="157" fromY="226" toX="688" toY="424" spline="False">\n'
    '            <AssociationName deltaX="0" deltaY="0" />\n'
    '            <SourceCardinality deltaX="0" deltaY="0" />\n'
    '            <DestinationCardinality deltaX="0" deltaY="0" />\n'
    '            <ModelLink name="" type="AGGREGATION" sourceId="" destinationId="" bidirectional="False" sourceCardinalityValue="" destinationCardinalityValue="" />\n'
    '        </UmlLink>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)
BASENAME:                         str  = 'AggregationTest'
AGGREGATION_XML_FILENAME:         str = f'{BASENAME}.xml'
AGGREGATION_FILENAME:             Path = Path(f'/tmp/{BASENAME}.udt')
DECOMPRESSED_AGGREGATION_PROJECT: Path = Path(f'/tmp/{AGGREGATION_XML_FILENAME}')

pyautogui.PAUSE = 0.5

AGGREGATION_FILENAME.unlink(missing_ok=True)
DECOMPRESSED_AGGREGATION_PROJECT.unlink(missing_ok=True)

if isAppRunning() is False:
    alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
else:
    makeAppActive()

    click(x=729, y=136)
    click(x=730, y=70)

    click(x=333, y=264)
    click(x=830, y=371)
    press('backspace', presses=12)
    write('Aggregator')
    # Click Ok button on dialog
    click(x=980, y=680)
    click(x=733, y=72)
    click(x=948, y=494)
    click(x=841, y=365)
    press('backspace', presses=12)
    write('Aggregated')
    click(x=972, y=681)
    click(x=1055, y=65)
    click(x=373, y=307)
    click(x=989, y=539)
    click(x=217, y=1226)
    click(x=121, y=1229)

    invokeSaveAsProject(projectFileName=str(AGGREGATION_FILENAME))

    success: bool = wasTestSuccessful(
        projectFileName=AGGREGATION_FILENAME,
        decompressedProjectFileName=DECOMPRESSED_AGGREGATION_PROJECT,
        goldenXml=GOLDEN_AGGREGATION_XML
    )

    displayAppropriateDialog(status=success)

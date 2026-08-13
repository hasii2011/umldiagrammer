#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes', 'opencv-python']
# ///
from pathlib import Path

import pyautogui
from pyautogui import press
from pyautogui import click
from pymsgbox import alert
from umlshapes.types.UmlPosition import UmlPosition

from tests.uitests.Common import BACKSPACES_CLEAR_CLASS_NAME
from tests.uitests.Common import PAUSE_AFTER_EACH_CALL
from tests.uitests.Common import displayAppropriateDialog

from tests.uitests.Common import isAppRunning
from tests.uitests.Common import makeAppActive
from tests.uitests.Common import wasTestSuccessful
from tests.uitests.SaveAsProject import SaveAsProject
from tests.uitests.locators.BaseLocator import Location
from tests.uitests.locators.ClassDialogLocator import ClassDialogLocator
from tests.uitests.locators.ToolBarIconLocator import ToolBarIconLocator
from tests.uitests.locators.UmlClassLocator import UmlClassLocator

#
# Removed the IDs;  Also, removed the ModelLink name
#
GOLDEN_AGGREGATION_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/AggregationTest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="113" height="90" x="199" y="152">\n'
    '            <ModelClass id="" name="TheAggregator" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlClass id="" width="88" height="90" x="549" y="447">\n'
    '            <ModelClass id="" name="Aggregated" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlLink id="" fromX="307" fromY="242" toX="549" toY="454" spline="False">\n'
    '            <AssociationName deltaX="0" deltaY="0" />\n'
    '            <SourceCardinality deltaX="0" deltaY="0" />\n'
    '            <DestinationCardinality deltaX="0" deltaY="30" />\n'
    '            <ModelLink name="" type="AGGREGATION" sourceId="" destinationId="" bidirectional="False" sourceCardinalityValue="src Card" destinationCardinalityValue="dst Card" />\n'
    '        </UmlLink>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)
BASENAME:                         str  = 'AggregationTest'
AGGREGATION_XML_FILENAME:         str = f'{BASENAME}.xml'
AGGREGATION_FILENAME:             Path = Path(f'/tmp/{BASENAME}.udt')
DECOMPRESSED_AGGREGATION_PROJECT: Path = Path(f'/tmp/{AGGREGATION_XML_FILENAME}')

LOC_WHERE_AGGREGATOR_IS_CREATED: UmlPosition = UmlPosition(x=475, y=255)
LOC_WHERE_AGGREGATED_IS_CREATED: UmlPosition = UmlPosition(x=825, y=550)

def renameClass(newClassName: str, locator: ClassDialogLocator):

    textInputLocation: Location = locator.classNameTextInput
    click(x=textInputLocation.x, y=textInputLocation.y)

    press(keys='backspace', presses=BACKSPACES_CLEAR_CLASS_NAME)
    pyautogui.typewrite(newClassName)


if __name__ == '__main__':

    pyautogui.PAUSE    = PAUSE_AFTER_EACH_CALL
    pyautogui.FAILSAFE = True

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        AGGREGATION_FILENAME.unlink(missing_ok=True)
        DECOMPRESSED_AGGREGATION_PROJECT.unlink(missing_ok=True)

        iconLocator:        ToolBarIconLocator = ToolBarIconLocator()
        classDialogLocator: ClassDialogLocator = ClassDialogLocator()
        umlClassLocator:    UmlClassLocator    = UmlClassLocator()

        newClassIconLocation: Location = iconLocator.newClass

        # Create the aggregator; Make name more different so locator can tell
        click(x=newClassIconLocation.x, y=newClassIconLocation.y)
        click(x=LOC_WHERE_AGGREGATOR_IS_CREATED.x, y=LOC_WHERE_AGGREGATOR_IS_CREATED.y)
        renameClass(newClassName='TheAggregator', locator=classDialogLocator)

        clickClassOkButton: Location = classDialogLocator.clickClassOkButton
        click(x=clickClassOkButton.x, y=clickClassOkButton.y)

        # Create the Aggregated
        click(x=newClassIconLocation.x, y=newClassIconLocation.y)
        click(x=LOC_WHERE_AGGREGATED_IS_CREATED.x, y=LOC_WHERE_AGGREGATED_IS_CREATED.y)
        renameClass(newClassName='Aggregated', locator=classDialogLocator)
        click(x=clickClassOkButton.x, y=clickClassOkButton.y)

        newAggregationLinkLocation: Location = iconLocator.aggregationLink
        click(x=newAggregationLinkLocation.x, y=newAggregationLinkLocation.y)

        aggregatorLocation: Location = umlClassLocator.aggregator
        click(x=aggregatorLocation.x, y=aggregatorLocation.y)
        print(f'{aggregatorLocation=}')

        aggregatedLocation: Location = umlClassLocator.aggregated
        click(x=aggregatedLocation.x, y=aggregatedLocation.y)
        print(f'{aggregatedLocation=}')

        saveAsProject: SaveAsProject = SaveAsProject()
        saveAsProject.execute(projectFileName=str(AGGREGATION_FILENAME))

        success: bool = wasTestSuccessful(
            projectFileName=AGGREGATION_FILENAME,
            decompressedProjectFileName=DECOMPRESSED_AGGREGATION_PROJECT,
            goldenXml=GOLDEN_AGGREGATION_XML
        )

        displayAppropriateDialog(status=success)

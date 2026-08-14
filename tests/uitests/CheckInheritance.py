#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes', 'opencv-python']
# ///

from pathlib import Path

import pyautogui
from pyautogui import click

from pymsgbox import alert

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.preferences.UmlPreferences import UmlPreferences


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
# Removed the IDs
#
GOLDEN_INHERITANCE_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/inheritancetest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="110" height="90" x="124" y="97">\n'
    '            <ModelClass id="" name="TheBaseClass" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlClass id="" width="72" height="90" x="624" y="397">\n'
    '            <ModelClass id="" name="SubClass" displayMethods="True" displayParameters="Unspecified" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="" />\n'
    '        </UmlClass>\n'
    '        <UmlLink id="" fromX="624" fromY="420" toX="234" toY="176" spline="False">\n'
    '            <ModelLink name="" type="INHERITANCE" sourceId="" destinationId="" bidirectional="False" sourceCardinalityValue="" destinationCardinalityValue="" />\n'
    '        </UmlLink>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)

BASENAME:                     str  = 'inheritancetest'
INHERITANCE_PROJECT_FILENAME: Path = Path(f'/tmp/{BASENAME}.udt')

INHERITANCE_XML_FILENAME:         str = f'{BASENAME}.xml'
DECOMPRESSED_INHERITANCE_PROJECT: Path = Path(f'/tmp/{INHERITANCE_XML_FILENAME}')

LOC_CREATE_BASE_CLASS: UmlPosition = UmlPosition(x=400, y=200)
LOC_CREATE_SUB_CLASS:  UmlPosition = UmlPosition(x=900, y=500)


SUBCLASS_NAME:    str = 'SubClass'
BASECLASS_NAME:   str = 'TheBaseClass'

if __name__ == '__main__':

    pyautogui.PAUSE   = PAUSE_AFTER_EACH_CALL
    pyautogui.FAILSAFE = True

    umlPreferences: UmlPreferences = UmlPreferences()

    INHERITANCE_PROJECT_FILENAME.unlink(missing_ok=True)
    DECOMPRESSED_INHERITANCE_PROJECT.unlink(missing_ok=True)

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        INHERITANCE_PROJECT_FILENAME.unlink(missing_ok=True)
        DECOMPRESSED_INHERITANCE_PROJECT.unlink(missing_ok=True)

        iconLocator:     ToolBarIconLocator = ToolBarIconLocator()
        umlClassLocator: UmlClassLocator    = UmlClassLocator()

        createClassPair(
            class1Location=LOC_CREATE_BASE_CLASS,
            class1Name=BASECLASS_NAME,
            class2Location=LOC_CREATE_SUB_CLASS,
            class2Name=SUBCLASS_NAME
        )

        #
        # Click on the Inheritance Link Icon
        #
        newInheritanceLinkLocation: Location = iconLocator.inheritanceLink
        click(x=newInheritanceLinkLocation.x, y=newInheritanceLinkLocation.y)

        subClassLocation: Location = umlClassLocator.subClass
        click(x=subClassLocation.x, y=subClassLocation.y)
        print(f'{subClassLocation=}')

        baseClassLocation: Location = umlClassLocator.baseClass
        click(x=baseClassLocation.x, y=baseClassLocation.y)
        print(f'{baseClassLocation=}')

        saveAsProject: SaveAsProject = SaveAsProject()
        saveAsProject.execute(projectFileName=str(INHERITANCE_PROJECT_FILENAME))

        success: bool = wasTestSuccessful(
            projectFileName=INHERITANCE_PROJECT_FILENAME,
            decompressedProjectFileName=DECOMPRESSED_INHERITANCE_PROJECT,
            goldenXml=GOLDEN_INHERITANCE_XML
        )

        displayAppropriateDialog(status=success)

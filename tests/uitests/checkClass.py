#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes', 'opencv-python', 'pyperclip']
# ///

import pyautogui

from os import sep as osSep

from pathlib import Path

from pyautogui import press
from pyautogui import click

from pyautogui import typewrite

from pymsgbox import alert

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlPosition import UmlPosition

from tests.uitests.ClassDialogLocator import ClassDialogLocator
from tests.uitests.ToolBarIconLocator import Location
from tests.uitests.ToolBarIconLocator import ToolBarIconLocator
from tests.uitests.common import BACKSPACES_CLEAR_CLASS_NAME
from tests.uitests.common import DOUBLE_CLICK_INTERVAL
from tests.uitests.common import TYPE_WRITE_INTERVAL
from tests.uitests.common import displayAppropriateDialog
from tests.uitests.common import invokeSaveAsProject
from tests.uitests.common import isAppRunning
from tests.uitests.common import makeAppActive
from tests.uitests.common import setupLogging
from tests.uitests.common import wasTestSuccessful


WELL_KNOWN_CLASS_NAME = 'ClassName1'

#
# Removed the IDs
#
GOLDEN_CLASS_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/UIClassTest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="325" height="150" x="444" y="247">\n'
    '            <ModelClass id="" name="ClassName1" displayMethods="True" displayParameters="Display Parameters" displayConstructor="Unspecified" displayDunderMethods="Unspecified" displayFields="True" displayStereotype="True" fileName="" description="">\n'
    '                <ModelMethod name="MethodName" visibility="PUBLIC" returnType="">\n'
    '                    <SourceCode />\n'
    '                    <ModelParameter name="floatParameter" parameterType="float" defaultValue="42.0" />\n'
    '                </ModelMethod>\n'
    '                <ModelField name="publicField" visibility="PUBLIC" fieldType="int" defaultValue="42" />\n'
    '            </ModelClass>\n'
    '        </UmlClass>\n'
    '    </UMLDiagram>\n'
    '</UmlProject>'
)

MATCH_BETWEEN_QUOTES: str = '"(.*?)"'
MATCH_STARTS_WITH_ID: str = f'id={MATCH_BETWEEN_QUOTES}'
EMPTY_ID:             str = ''


LOC_CREATE_CLASS:       UmlPosition = UmlPosition(x=680, y=370)
LOC_CLASS_NAME:         UmlPosition = UmlPosition(x=783, y=370)
LOC_CLICK_SAVE_PROJECT: UmlPosition = UmlPosition(x=390, y=70)

BASENAME:                   str = 'UIClassTest'
CLASS_PROJECT_FILENAME:     Path = Path(f'{osSep}tmp{osSep}{BASENAME}.udt')

CLASS_XML_FILENAME:         str = f'{BASENAME}.xml'
DECOMPRESSED_CLASS_PROJECT: Path = Path(f'/tmp/{CLASS_XML_FILENAME}')

HACK_ADJUST_ADD_METHOD_BUTTON_Y: int = 40
HACK_ADJUST_ADD_FIELD_BUTTON_Y:  int = 40

def addParameterMethod(dialogLocator: ClassDialogLocator):

    addParameterButtonLocation: Location = dialogLocator.addParameterButton
    click(x=addParameterButtonLocation.x, y=addParameterButtonLocation.y)

    parameterNameLocation: Location = dialogLocator.parameterNameTextInput
    click(x=parameterNameLocation.x, y=parameterNameLocation.y + 5, clicks=2, interval=DOUBLE_CLICK_INTERVAL)
    press('backspace', presses=len(defaultMethodName))
    typewrite('floatParameter', interval=TYPE_WRITE_INTERVAL)

    press('tab')
    typewrite('float', interval=TYPE_WRITE_INTERVAL)

    press('tab')
    typewrite('42.0', interval=TYPE_WRITE_INTERVAL)

    parameterOkButtonLocation: Location = dialogLocator.clickParameterOkButton
    click(x=parameterOkButtonLocation.x, y=parameterOkButtonLocation.y + 10)


def addPublicField(dialogLocator: ClassDialogLocator):

    addFieldButtonLocation: Location = dialogLocator.clickAddFieldButton
    click(x=addFieldButtonLocation.x, y=addFieldButtonLocation.y + HACK_ADJUST_ADD_FIELD_BUTTON_Y)

    publicFieldRBLocation: Location = dialogLocator.publicFieldRadioButton
    click(x=publicFieldRBLocation.x, y=publicFieldRBLocation.y)

    press('backspace')      # text input still has focus

    typewrite('publicField', interval=TYPE_WRITE_INTERVAL)
    press('right', presses=3)

    press('tab')
    typewrite('int', interval=TYPE_WRITE_INTERVAL)

    press('tab')
    typewrite('42', interval=TYPE_WRITE_INTERVAL)

    fieldOkButtonLocation: Location = dialogLocator.clickFieldOkButton
    click(x=fieldOkButtonLocation.x, y=fieldOkButtonLocation.y)


if __name__ == '__main__':

    pyautogui.PAUSE = 0.5
    pyautogui.FAILSAFE = True

    setupLogging()

    umlPreferences: UmlPreferences = UmlPreferences()

    defaultMethodName:     str   = umlPreferences.defaultNameMethod
    defaultFieldName:      str   = umlPreferences.defaultNameField

    CLASS_PROJECT_FILENAME.unlink(missing_ok=True)
    DECOMPRESSED_CLASS_PROJECT.unlink(missing_ok=True)

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        iconLocator:        ToolBarIconLocator = ToolBarIconLocator()
        classDialogLocator: ClassDialogLocator = ClassDialogLocator()

        location: Location = iconLocator.newClass
        click(x=location.x,   y=location.y)

        click(x=LOC_CREATE_CLASS.x,     y=LOC_CREATE_CLASS.y)

        textInputLocation: Location = classDialogLocator.classNameTextInput
        click(x=location.x, y=location.y)

        press('backspace', BACKSPACES_CLEAR_CLASS_NAME)
        typewrite(WELL_KNOWN_CLASS_NAME)

        addMethodButtonLocation: Location = classDialogLocator.addMethodButton
        click(x=addMethodButtonLocation.x, y=addMethodButtonLocation.y + HACK_ADJUST_ADD_METHOD_BUTTON_Y)  # Cheat from center

        addParameterMethod(dialogLocator=classDialogLocator)

        methodOkButtonLocation: Location = classDialogLocator.clickMethodOkButton
        click(x=methodOkButtonLocation.x,    y=methodOkButtonLocation.y)

        addPublicField(dialogLocator=classDialogLocator)

        clickClassOkButton: Location = classDialogLocator.clickClassOkButton
        click(x=clickClassOkButton.x, y=clickClassOkButton.y)

        classShapeLocation: Location = classDialogLocator.classShape
        click(x=classShapeLocation.x,  y=classShapeLocation.y, button='right')

        classContextMenuLocation: Location = classDialogLocator.classShapeContextMenu
        click(x=classContextMenuLocation.x, y=classContextMenuLocation.y)
        #
        invokeSaveAsProject(projectFileName=str(CLASS_PROJECT_FILENAME))
        #
        # success: bool = wasTestSuccessful(
        #     projectFileName=CLASS_PROJECT_FILENAME,
        #     decompressedProjectFileName=DECOMPRESSED_CLASS_PROJECT,
        #     goldenXml=GOLDEN_CLASS_XML
        # )
        #
        # displayAppropriateDialog(status=success)

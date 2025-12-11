#!/usr/bin/env python

import pyautogui

from pathlib import Path

from pyautogui import press
from pyautogui import click

from pyautogui import typewrite

from pymsgbox import alert

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlPosition import UmlPosition

from tests.uitests.common import DOUBLE_CLICK_INTERVAL
from tests.uitests.common import LOC_CLASS_TOOL_BAR
from tests.uitests.common import TYPE_WRITE_INTERVAL
from tests.uitests.common import displayAppropriateDialog
from tests.uitests.common import invokeSaveAsProject
from tests.uitests.common import isAppRunning
from tests.uitests.common import makeAppActive
from tests.uitests.common import wasTestSuccessful

#
# Removed the IDs
#
GOLDEN_CLASS_XML: str = (
    "<?xml version='1.0' encoding='iso-8859-1'?>\n"
    '<UmlProject fileName="/private/tmp/UIClassTest.udt" version="14.0" codePath=".">\n'
    '    <UMLDiagram documentType="Class Document" title="Class Diagram" scrollPositionX="0" scrollPositionY="0" pixelsPerUnitX="20" pixelsPerUnitY="20">\n'
    '        <UmlClass id="" width="325" height="150" x="420" y="271">\n'
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


LOC_CREATE_CLASS:           UmlPosition = UmlPosition(x=680, y=370)
LOC_CLICK_ADD_METHOD:       UmlPosition = UmlPosition(x=600, y=620)
LOC_CLICK_ADD_PARAMETER:    UmlPosition = UmlPosition(x=600, y=565)
LOC_CLICK_ADD_FIELD:        UmlPosition = UmlPosition(x=595, y=490)

LOC_CLICK_PARAMETER_NAME:   UmlPosition = UmlPosition(x=645, y=395)
LOC_CLICK_PARAMETER_TYPE:   UmlPosition = UmlPosition(x=729, y=398)

LOC_CLICK_PARAMETER_VALUE:  UmlPosition = UmlPosition(x=860, y=395)
LOC_CLICK_PARAMETER_OK:     UmlPosition = UmlPosition(x=855, y=445)

LOC_CLICK_PUBLIC_FIELD:     UmlPosition = UmlPosition(x=570, y=366)
LOC_CLICK_FIELD_NAME:       UmlPosition = UmlPosition(x=715, y=395)
LOC_CLICK_FIELD_TYPE:       UmlPosition = UmlPosition(x=805, y=395)
LOC_CLICK_FIELD_VALUE:      UmlPosition = UmlPosition(x=905, y=395)
LOC_CLICK_FIELD_OK:         UmlPosition = UmlPosition(x=915, y=455)

LOC_CLICK_METHOD_OK:        UmlPosition = UmlPosition(x=950, y=605)
LOC_CLICK_CLASS_OK:         UmlPosition = UmlPosition(x=980, y=685)

LOC_RIGHT_CLICK_CLASS:       UmlPosition = UmlPosition(x=740, y=440)
LOC_CLICK_PARAMETER_DISPLAY: UmlPosition = UmlPosition(x=797, y=517)

LOC_CLICK_SAVE_PROJECT:      UmlPosition = UmlPosition(x=390, y=70)
LOC_CLICK_SAVE_AS_NAME:      UmlPosition = UmlPosition(x=1379, y=333)
LOC_CLICK_SAVE_BUTTON:       UmlPosition = UmlPosition(x=1690, y=745)

BASENAME:                   str = 'UIClassTest'
CLASS_PROJECT_FILENAME:     Path = Path(f'/tmp/{BASENAME}.udt')

CLASS_XML_FILENAME:         str = f'{BASENAME}.xml'
DECOMPRESSED_CLASS_PROJECT: Path = Path(f'/tmp/{CLASS_XML_FILENAME}')


def addParameterMethod():

    click(x=LOC_CLICK_ADD_PARAMETER.x, y=LOC_CLICK_ADD_PARAMETER.y)
    click(x=LOC_CLICK_PARAMETER_NAME.x, y=LOC_CLICK_PARAMETER_NAME.y, clicks=2, interval=DOUBLE_CLICK_INTERVAL)
    press('backspace', presses=len(defaultMethodName))
    typewrite('floatParameter', interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_PARAMETER_TYPE.x, y=LOC_CLICK_PARAMETER_TYPE.y)
    typewrite('float', interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_PARAMETER_VALUE.x, y=LOC_CLICK_PARAMETER_VALUE.y)
    typewrite('42.0', interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_PARAMETER_OK.x, y=LOC_CLICK_PARAMETER_OK.y)


def addPublicField():

    click(x=LOC_CLICK_ADD_FIELD.x, y=LOC_CLICK_ADD_FIELD.y)
    click(x=LOC_CLICK_PUBLIC_FIELD.x, y=LOC_CLICK_PUBLIC_FIELD.y)

    click(x=LOC_CLICK_FIELD_NAME.x, y=LOC_CLICK_FIELD_NAME.y)
    press('backspace', presses=len(defaultFieldName))
    typewrite('publicField', interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_FIELD_TYPE.x, y=LOC_CLICK_FIELD_TYPE.y)
    typewrite('int', interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_FIELD_VALUE.x, y=LOC_CLICK_FIELD_VALUE.y)
    typewrite('42', interval=TYPE_WRITE_INTERVAL)
    click(x=LOC_CLICK_FIELD_OK.x, y=LOC_CLICK_FIELD_OK.y)


if __name__ == '__main__':

    pyautogui.PAUSE = 0.5

    umlPreferences: UmlPreferences = UmlPreferences()

    defaultMethodName:     str   = umlPreferences.defaultNameMethod
    defaultFieldName:      str   = umlPreferences.defaultNameField

    CLASS_PROJECT_FILENAME.unlink(missing_ok=True)
    DECOMPRESSED_CLASS_PROJECT.unlink(missing_ok=True)

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        click(x=LOC_CLASS_TOOL_BAR.x,   y=LOC_CLASS_TOOL_BAR.y)
        click(x=LOC_CREATE_CLASS.x,     y=LOC_CREATE_CLASS.y)

        click(x=LOC_CLICK_ADD_METHOD.x, y=LOC_CLICK_ADD_METHOD.y)
        addParameterMethod()
        click(x=LOC_CLICK_METHOD_OK.x,    y=LOC_CLICK_METHOD_OK.y)

        addPublicField()
        click(x=LOC_CLICK_CLASS_OK.x,     y=LOC_CLICK_CLASS_OK.y)

        click(x=LOC_RIGHT_CLICK_CLASS.x,       y=LOC_RIGHT_CLICK_CLASS.y, button='right')
        click(x=LOC_CLICK_PARAMETER_DISPLAY.x, y=LOC_CLICK_PARAMETER_DISPLAY.y)

        invokeSaveAsProject(projectFileName=str(CLASS_PROJECT_FILENAME))

        success: bool = wasTestSuccessful(
            projectFileName=CLASS_PROJECT_FILENAME,
            decompressedProjectFileName=DECOMPRESSED_CLASS_PROJECT,
            goldenXml=GOLDEN_CLASS_XML
        )

        displayAppropriateDialog(status=success)

#!/usr/bin/env python

from pathlib import Path

import pyautogui
from pyautogui import click
from pyautogui import press
from pyautogui import typewrite

from pymsgbox import alert

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.preferences.UmlPreferences import UmlPreferences

from tests.uitests.common import LOC_CLASS_TOOL_BAR
from tests.uitests.common import LOC_TOOLBAR_Y
from tests.uitests.common import DOUBLE_CLICK_INTERVAL
from tests.uitests.common import TYPE_WRITE_INTERVAL

from tests.uitests.common import invokeSaveAsProject
from tests.uitests.common import isAppRunning
from tests.uitests.common import makeAppActive

BASENAME:                     str = 'UIInheritanceTest'
INHERITANCE_PROJECT_FILENAME: Path = Path(f'/tmp/{BASENAME}.udt')

INHERITANCE_XML_FILENAME:         str = f'{BASENAME}.xml'
DECOMPRESSED_INHERITANCE_PROJECT: Path = Path(f'/tmp/{INHERITANCE_XML_FILENAME}')

LOC_INHERITANCE_TOOL_BAR: UmlPosition = UmlPosition(x=935, y=LOC_TOOLBAR_Y)

LOC_CREATE_BASE_CLASS:   UmlPosition = UmlPosition(x=400, y=200)
LOC_CLICK_BASE_CLASS_OK: UmlPosition = UmlPosition(x=980, y=690)

LOC_CREATE_SUB_CLASS:        UmlPosition = UmlPosition(x=900, y=500)
LOC_CLICK_SUBCLASS_CLASS_OK: UmlPosition = LOC_CLICK_BASE_CLASS_OK

LOC_CLASS_NAME:  UmlPosition = UmlPosition(x=770, y=365)

CHOOSE_SUBCLASS:  UmlPosition = UmlPosition(x=935, y=540)
CHOOSE_BASECLASS: UmlPosition = UmlPosition(x=440, y=235)

SUBCLASS_NAME:    str = 'SubClass'
BASECLASS_NAME:   str = 'BaseClass'
ADJUST_FOR_COUNT: int = 1

def createBaseClass(eraseName: str):
    click(x=LOC_CLASS_TOOL_BAR.x,      y=LOC_CLASS_TOOL_BAR.y)
    click(x=LOC_CREATE_BASE_CLASS.x,   y=LOC_CREATE_BASE_CLASS.y)

    click(x=LOC_CLASS_NAME.x, y=LOC_CLASS_NAME.y, clicks=2, interval=DOUBLE_CLICK_INTERVAL)
    press('backspace', presses=len(eraseName) + ADJUST_FOR_COUNT)
    typewrite(BASECLASS_NAME, interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_BASE_CLASS_OK.x, y=LOC_CLICK_BASE_CLASS_OK.y)


def createSubClass(eraseName: str):
    click(x=LOC_CLASS_TOOL_BAR.x,          y=LOC_CLASS_TOOL_BAR.y)
    click(x=LOC_CREATE_SUB_CLASS.x,        y=LOC_CREATE_SUB_CLASS.y)

    click(x=LOC_CLASS_NAME.x, y=LOC_CLASS_NAME.y, clicks=2, interval=DOUBLE_CLICK_INTERVAL)
    press('backspace', presses=len(eraseName) + ADJUST_FOR_COUNT)
    typewrite(SUBCLASS_NAME, interval=TYPE_WRITE_INTERVAL)

    click(x=LOC_CLICK_SUBCLASS_CLASS_OK.x, y=LOC_CLICK_SUBCLASS_CLASS_OK.y)


if __name__ == '__main__':

    pyautogui.PAUSE = 0.5

    umlPreferences: UmlPreferences = UmlPreferences()

    defaultClassName: str = umlPreferences.defaultClassName

    INHERITANCE_PROJECT_FILENAME.unlink(missing_ok=True)
    DECOMPRESSED_INHERITANCE_PROJECT.unlink(missing_ok=True)

    if isAppRunning() is False:
        alert(text='The diagrammer is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()

        createBaseClass(defaultClassName)
        createSubClass(defaultClassName)

        click(x=LOC_INHERITANCE_TOOL_BAR.x, y=LOC_INHERITANCE_TOOL_BAR.y)
        click(x=CHOOSE_SUBCLASS.x, y=CHOOSE_SUBCLASS.y)
        click(x=CHOOSE_BASECLASS.x, y=CHOOSE_BASECLASS.y)

        invokeSaveAsProject(projectFileName=str(INHERITANCE_PROJECT_FILENAME))

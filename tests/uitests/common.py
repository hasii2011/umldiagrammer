
from typing import List

import zlib

from pathlib import Path

from re import findall
from re import sub as regExSub

from difflib import unified_diff

from PIL import ImageGrab
from PIL.Image import Image

from pyautogui import moveTo
from pyautogui import click
from pyautogui import press
from pyautogui import typewrite

from pymsgbox import alert

from umlshapes.types.UmlPosition import UmlPosition

from umldiagrammer.DiagrammerTypes import DIAGRAMMER_IN_TEST_MODE

MATCH_BETWEEN_QUOTES: str = '"(.*?)"'
MATCH_STARTS_WITH_ID: str = f'id={MATCH_BETWEEN_QUOTES}'
SOURCE_ID:            str = f'sourceId={MATCH_BETWEEN_QUOTES}'
DESTINATION_ID:       str = f'destinationId={MATCH_BETWEEN_QUOTES}'

MATCH_STARTS_WITH_SRC_ID: str = f'sourceId={MATCH_BETWEEN_QUOTES}'
MATCH_STARTS_WITH_DST_DI: str = f'destinationId={MATCH_BETWEEN_QUOTES}'

EMPTY_ID:             str = ''

LEFT:                   str   = 'left'
DRAG_DURATION:          float = 0.5
TYPE_WRITE_INTERVAL:    float = 0.1
DOUBLE_CLICK_INTERVAL:  float = 0.2

LOC_TOOLBAR_Y: int = 65

LOC_CLASS_TOOL_BAR:         UmlPosition = UmlPosition(x=730, y=LOC_TOOLBAR_Y)

LOC_CLICK_SAVE_PROJECT:      UmlPosition = UmlPosition(x=390, y=70)
LOC_CLICK_SAVE_AS_NAME:      UmlPosition = UmlPosition(x=1379, y=333)
LOC_CLICK_SAVE_BUTTON:       UmlPosition = UmlPosition(x=1690, y=745)


def isAppRunning() -> bool:
    answer: bool = False

    if DIAGRAMMER_IN_TEST_MODE.exists() is True:
        answer = True

    return answer

def makeAppActive():
    # Make UML Diagrammer Active
    moveTo(250, 110)
    click()

def pullDownViewMenu():
    # Pull down view menu
    click(220, 20, button=LEFT)

def takeCompletionScreenShot(imagePath: Path):

    imagePath.unlink(missing_ok=True)

    left:   int = 18
    top:    int = 39
    right:  int = 1030
    bottom: int = 730

    bbox = (left, top, right, bottom)

    # Capture the specified region
    screenshot: Image = ImageGrab.grab(bbox)
    screenshot.save(imagePath, 'png')

def decompress(inputFileName: Path, outputFileName: Path):
    """
    Takes a zlib compressed file and turns it into a text file
    Args:
        inputFileName:   The compressed file
        outputFileName:  The decompressed text file

    """
    try:
        with open(inputFileName, "rb") as inputFile:
            # print(f'Inflating: {inputFileName}')
            compressedData: bytes = inputFile.read()

            # print(f'Bytes read: {len(compressedData)}')
            xmlBytes:  bytes = zlib.decompress(compressedData)  # has b '....' around it
            xmlString: str   = xmlBytes.decode()

            # print(f'Writing {len(xmlString)} bytes to {outputFileName}')
            with open(outputFileName, 'w') as outputFile:
                outputFile.write(xmlString)
    except (ValueError, Exception) as e:
        print(f'Error:  {e}')

def invokeSaveAsProject(projectFileName: str):

    click(x=LOC_CLICK_SAVE_PROJECT.x, y=LOC_CLICK_SAVE_PROJECT.y)
    moveTo(x=LOC_CLICK_SAVE_AS_NAME.x, y=LOC_CLICK_SAVE_AS_NAME.y, duration=3.0)

    click(x=LOC_CLICK_SAVE_AS_NAME.x, y=LOC_CLICK_SAVE_AS_NAME.y)

    press('backspace', presses=len('untitled'))
    typewrite(projectFileName, interval=TYPE_WRITE_INTERVAL)
    press('enter')
    click(x=LOC_CLICK_SAVE_BUTTON.x, y=LOC_CLICK_SAVE_BUTTON.y)

def wasTestSuccessful(projectFileName: Path, decompressedProjectFileName: Path, goldenXml: str) -> bool:

    answer: bool = True

    decompress(inputFileName=projectFileName, outputFileName=decompressedProjectFileName)

    generatedXmlFile: Path = Path(decompressedProjectFileName)
    generatedXml:     str  = generatedXmlFile.read_text()

    matches: List[str] = findall(MATCH_STARTS_WITH_ID, generatedXml)

    fixedXml: str = generatedXml
    for idStr in matches:
        fixedXml = regExSub(pattern=idStr, repl=EMPTY_ID, string=fixedXml)

    if fixedXml != goldenXml:
        diff = unified_diff(
            goldenXml.splitlines(),
            fixedXml.splitlines(),
            lineterm='',
            fromfile='Golden',
            tofile='Generated'
        )
        print('\n'.join(list(diff)))
        answer = False

    return answer

def displayAppropriateDialog(status: bool):

    if status is True:
        title: str = 'Success'
        message: str = 'You are a great programmer'
    elif status is False:
        title = 'Failure'
        message = 'You have failed as a programmer.  Check the console output'
    else:
        assert False, 'Developer error'

    alert(text=message, title=title, button='OK')

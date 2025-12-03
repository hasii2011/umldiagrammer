
import zlib

from pathlib import Path

from PIL import ImageGrab
from PIL.Image import Image

from pyautogui import moveTo
from pyautogui import click

from umldiagrammer.DiagrammerTypes import DIAGRAMMER_IN_TEST_MODE

LEFT:          str   = 'left'
DRAG_DURATION: float = 0.5

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

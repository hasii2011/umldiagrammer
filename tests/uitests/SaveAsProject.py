
from logging import Logger
from logging import getLogger

from time import sleep as pySleep

from subprocess import run as subProcessRun

from pyautogui import click
from pyautogui import hotkey
from pyautogui import keyUp
from pyautogui import press

from tests.uitests.ToolBarClicker import ToolBarClicker
from tests.uitests.locators.BaseLocator import Location
from tests.uitests.locators.CommonImageLocator import CommonImageLocator

POST_CONFIRM_GOTO_FOLDER_DIALOG = 1.2

SAVE_DIALOG_DELAY:               float = 2.0
SAVE_AS_TEXT_INPUT_FOCUS_DELAY:  float = 0.2
INVOKE_GOTO_FOLDER_DIALOG_DELAY: float = 0.8
POST_APPLE_SCRIPT_DELAY:         float = 0.3

APPLE_SCRIPT_SEND_KEYSTROKES: str = 'tell application "System Events" to keystroke'
class SaveAsProject:
    """
    A hacked up set of code generated with help from various AntiGravity
    LLMs.  After going round and round they settled on the AppleScript
    hack/workaround

    According to Claude Sonnet 4.6

    Also, typewrite() does not support all characters — notably /, ., and
    uppercase letters via shift — it can misfire key
    combos that trigger system shortcuts.

    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._commonImageLocator: CommonImageLocator = CommonImageLocator()
        self._toolBarClicker:     ToolBarClicker     = ToolBarClicker()

    def execute(self, projectFileName: str):

        self.logger.info(f'{projectFileName=}')
        self._releasePotentialStuckModifierKeys()
        self._pressSaveProject()
        self._focusOnTheSaveAsTextInput()
        self._invokeGoToFolderDialog()
        #
        # No need to click the text box. It natively has focus.
        # No need to backspace. The text is highlighted.
        #
        self._hackMethodToTypeInPathName(projectFileName=projectFileName)

    def _releasePotentialStuckModifierKeys(self):
        """
        Workaround:

        Sometimes during a long script, PyAutoGUI loses track of its internal state
        and fails to release the modifier keys.
        """

        keyUp('shift')
        keyUp('command')
        keyUp('option')
        keyUp('ctrl')

    def _pressSaveProject(self):
        """
        Waits for the Save dialog to fully appear
        """
        self._toolBarClicker.clickSaveProject()

        self.logger.info(f'Wait {SAVE_DIALOG_DELAY} seconds for Save dialog to appear')
        pySleep(SAVE_DIALOG_DELAY)

    def _focusOnTheSaveAsTextInput(self):

        textInputLocation: Location = self._commonImageLocator.saveAsProjectNameTextInput
        click(x=textInputLocation.x, y=textInputLocation.y)

        pySleep(SAVE_AS_TEXT_INPUT_FOCUS_DELAY)

    def _invokeGoToFolderDialog(self):

        hotkey('command', 'shift', 'g')
        pySleep(INVOKE_GOTO_FOLDER_DIALOG_DELAY)

    def _hackMethodToTypeInPathName(self, projectFileName: str):
        """
        PyAutoGUI's keyboard emulation is fatally corrupted by this point in checkClass.py.
        Bypass it entirely and use macOS native AppleScript to type the string.

        """
        applescript: str = f'{APPLE_SCRIPT_SEND_KEYSTROKES} "{projectFileName}"'

        subProcessRun(['osascript', '-e', applescript])

        pySleep(POST_APPLE_SCRIPT_DELAY)

        self._pressReturn()     # Confirm 'Go to Folder' dialog
        pySleep(POST_CONFIRM_GOTO_FOLDER_DIALOG)
        self._pressReturn()     # Confirm the 'Save As' dialog

    def _pressReturn(self):
        press('return')

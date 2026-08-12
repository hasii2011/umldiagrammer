#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes', 'opencv-python', 'pyperclip']
# ///
from os import sep as osSep

from pathlib import Path

import pyautogui

from tests.uitests.common import invokeSaveAsProject
from tests.uitests.common import setupLogging

BASENAME:                   str = 'uiclasstest'
CLASS_PROJECT_FILENAME:     Path = Path(f'{osSep}tmp{osSep}{BASENAME}.udt')

if __name__ == '__main__':

    pyautogui.PAUSE = 0.5
    pyautogui.FAILSAFE = True

    setupLogging()

    invokeSaveAsProject(projectFileName=str(CLASS_PROJECT_FILENAME))

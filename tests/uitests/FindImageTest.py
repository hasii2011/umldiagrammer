#!/usr/bin/env python
# /// script
# dependencies = ['pillow', 'pyautogui', 'umlshapes', 'opencv-python']
# ///
from pyautogui import ImageNotFoundException
from pyautogui import locateCenterOnScreen

if __name__ == '__main__':

    print(f'Remember.  Image size has to match')
    try:
        pt = locateCenterOnScreen('ToolbarClassIcon.png', confidence=0.9)
        print(f'({pt.x},{pt.y})')
    except ImageNotFoundException:
        print('Where the heck is the image')

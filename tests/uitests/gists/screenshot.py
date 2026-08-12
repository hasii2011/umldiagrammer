#!/usr/bin/env python
# /// script
# dependencies = ['pyautogui', 'pillow', 'umlshapes']
# ///
from PIL.PngImagePlugin import PngImageFile

from pyautogui import screenshot

if __name__ == '__main__':

    img: PngImageFile = screenshot('my_screenshot.png')

    img.save('screenshot.png')
    print(f'{img}')

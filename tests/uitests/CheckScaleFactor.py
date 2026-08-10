#!/usr/bin/env python
# /// script
# dependencies = ['pillow', 'pyautogui', 'umlshapes', 'opencv-python']
# ///


from PIL import ImageGrab
from pyautogui import size

logicalWidth:  int = size().width
physicalWidth: int = ImageGrab.grab().width
scaleFactor:   int = int(physicalWidth / logicalWidth)  # Will be 2 on HiDPI/Retina

print(f'{logicalWidth=} {physicalWidth=} {scaleFactor=}')

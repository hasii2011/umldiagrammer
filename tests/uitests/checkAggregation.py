#!/usr/bin/env python
# /// script
# dependencies = ["pyautogui"]
# ///

import pyautogui
from pyautogui import write
from pyautogui import press
from pyautogui import click


pyautogui.PAUSE = 0.5

click(x=729, y=136)
click(x=730, y=70)


click(x=333, y=264)
click(x=830, y=371)
press('backspace', presses=12)
write('Aggregator')
# Click Ok button on dialog
click(x=980, y=680)
click(x=733, y=72)
click(x=948, y=494)
click(x=841, y=365)
press('backspace', presses=12)
write('Aggregated')
click(x=972, y=681)
click(x=1055, y=65)
click(x=373, y=307)
click(x=989, y=539)
click(x=217, y=1226)
click(x=121, y=1229)

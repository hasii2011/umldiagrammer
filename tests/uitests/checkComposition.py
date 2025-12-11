#!/usr/bin/env python
# /// script
# dependencies = ["pyautogui"]
# ///
"""
From the command line and if you have `uv` installed
you can execute this script as follow:

uv run transcribed.py
"""

import pyautogui
from pyautogui import write
from pyautogui import press
from pyautogui import click


pyautogui.PAUSE = 0.5

click(x=770, y=323)
click(x=729, y=70)
click(x=473, y=331)
click(x=826, y=366)
press('backspace', presses=13)
write('Composer')
click(x=985, y=696)
click(x=728, y=66)
click(x=880, y=500)
click(x=782, y=364)
press('backspace', presses=12)
write('Composed')
click(x=982, y=681)
click(x=1022, y=72)
click(x=510, y=371)
click(x=911, y=543)

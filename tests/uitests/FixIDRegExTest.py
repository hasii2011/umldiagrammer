#!/usr/bin/env python
# /// script
# dependencies = ['pillow', 'umlshapes', 'pyautogui']
# ///

from typing import List

from pathlib import Path

from re import findall
from re import sub as regExSub

from tests.uitests.common import EMPTY_ID
from tests.uitests.common import ID_NAME_MATCH


def runComparison(xmlToFix: str, patternToMatch: str) -> str:
    """

    Args:
        xmlToFix:
        patternToMatch:

    Returns:

    """
    matchList: List[str] = findall(patternToMatch, xmlToFix)

    correctedXml: str = xmlToFix
    for matchedIdStr in matchList:
        correctedXml = regExSub(pattern=matchedIdStr, repl=EMPTY_ID, string=correctedXml)

    return correctedXml


if __name__ == '__main__':

    generatedXmlFile: Path = Path('/tmp/AggregationTest.xml')
    generatedXml: str = generatedXmlFile.read_text()

    fixedXml = runComparison(xmlToFix=generatedXml, patternToMatch=ID_NAME_MATCH)
    print(fixedXml)

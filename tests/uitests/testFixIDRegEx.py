#!/usr/bin/env python
# /// script
# dependencies = ["pillow", "umlshapes"]
# ///

from typing import List

from pathlib import Path

from re import findall
from re import sub as regExSub

from tests.uitests.common import EMPTY_ID
from tests.uitests.common import MATCH_STARTS_WITH_ID

generatedXmlFile: Path = Path('/tmp/UIInheritanceTest.xml')
generatedXml: str = generatedXmlFile.read_text()

matches: List[str] = findall(MATCH_STARTS_WITH_ID, generatedXml)

fixedXml: str = generatedXml
for idStr in matches:
    fixedXml = regExSub(pattern=idStr, repl=EMPTY_ID, string=fixedXml)

lines = fixedXml.splitlines()
for line in lines:
    print(line)

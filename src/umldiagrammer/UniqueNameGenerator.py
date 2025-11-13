
from typing import List
from typing import NewType

DISCRIMINATOR_START: str = '('
DISCRIMINATOR_END:   str = ')'

SPLIT_CHARACTER: str = DISCRIMINATOR_START

NameList = NewType('NameList', List[str])

def createUniqueName(nameToCheck: str, names: NameList, discriminator: int = 0) -> str:
    """

    BTW:
        * I HATE !!! recursion
        * I HATE internal methods
        * Much Hate in this utility class

    Args:
        nameToCheck:    The name to check
        names:          The list of potential collisions
        discriminator:  An integer that keeps getting bumped

    Returns:  A unique name based on the discriminator counter
    """

    def stripDiscriminatorText(name: str) -> str:
        return name.split(SPLIT_CHARACTER, 1)[0]

    if nameToCheck in names:
        plainName: str = stripDiscriminatorText(nameToCheck)
        discriminator += 1
        discriminatedName = f'{plainName}{DISCRIMINATOR_START}{discriminator}{DISCRIMINATOR_END}'
        return createUniqueName(discriminatedName, names, discriminator)
    else:
        return nameToCheck


from typing import Union

from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlLink import UmlLink
from umlshapes.shapes.UmlClass import UmlClass

DoableObjectType  = Union[UmlClass, UmlLink, UmlInterface]

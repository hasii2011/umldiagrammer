
from typing import Union

from umlshapes.links.UmlLink import UmlLink
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.links.UmlInterface import UmlInterface

DoableObjectType  = Union[UmlClass, UmlNote, UmlText, UmlLink, UmlInterface]

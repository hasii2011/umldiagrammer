
from dataclasses import dataclass

from umlmodel.Interface import Interfaces

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlPosition import UmlPosition


@dataclass
class LollipopCreationData:
    requestingFrame:    ClassDiagramFrame
    requestingUmlClass: UmlClass
    interfaces:         Interfaces
    perimeterPoint:     UmlPosition

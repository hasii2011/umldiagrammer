
from dataclasses import dataclass

from pyutmodelv2.PyutInterface import PyutInterfaces

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlPosition import UmlPosition


@dataclass
class LollipopCreationData:
    requestingFrame:    ClassDiagramFrame
    requestingUmlClass: UmlClass
    pyutInterfaces:     PyutInterfaces
    perimeterPoint:     UmlPosition

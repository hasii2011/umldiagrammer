
from typing import Dict
from typing import NewType

from dataclasses import dataclass

from umlshapes.frames.DiagramFrame import FrameId
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlio.IOTypes import UmlProject
from umlio.IOTypes import UmlDocumentTitle

from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId


@dataclass
class ProjectInformation:
    umlProject: UmlProject
    modified:   bool = False


FrameIdMap             = NewType('FrameIdMap',             Dict[FrameId, ClassDiagramFrame | UseCaseDiagramFrame | SequenceDiagramFrame])
FrameIdToTitleMap      = NewType('FrameIdToTitleMap',      Dict[FrameId, UmlDocumentTitle])
UmlDocumentTitleToPage = NewType('UmlDocumentTitleToPage', Dict[UmlDocumentTitle, int])

APPLICATION_FRAME_ID: UniqueId = UniqueId('FEED ZOMBIES')
EDIT_MENU_HANDLER_ID: UniqueId = UniqueId('REALITY DENIAL')
NOTEBOOK_ID:          UniqueId = UniqueId('SURRENDER MONKEYS')

HACK_ADJUST_EXIT_HEIGHT: int = 52    # TODO: I think this is the status bar and the title area

APP_MODE: str = 'APP_MODE'

UmlShape = UmlActor | UmlNote | UmlText | UmlUseCase | UmlClass
UmlLinkType = UmlInheritance | UmlInterface

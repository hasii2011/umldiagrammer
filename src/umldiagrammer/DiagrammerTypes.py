
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId

from typing import Dict
from typing import NewType

from umlshapes.frames.DiagramFrame import FrameId

from umlio.IOTypes import UmlDocumentTitle

FrameIdMap             = NewType('FrameIdMap',             Dict[FrameId, UmlDocumentTitle])
UmlDocumentTitleToPage = NewType('UmlDocumentTitleToPage', Dict[UmlDocumentTitle, int])

APPLICATION_FRAME_ID: UniqueId = UniqueId('FEED ZOMBIES')


from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_MENU

from wx import Menu
from wx import CommandEvent

from wx.lib.sized_controls import SizedFrame

from umlshapes.frames.DiagramFrame import FrameId

from umldiagrammer.pubsubengine.MessageType import MessageType
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.DiagrammerTypes import EDIT_MENU_HANDLER_ID
from umldiagrammer.menuHandlers.BaseMenuHandler import BaseMenuHandler

NO_FRAME_ID = cast(FrameId, None)

class EditMenuHandler(BaseMenuHandler):
    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        from wx import ID_UNDO
        from wx import ID_REDO
        from wx import ID_CUT
        from wx import ID_COPY
        from wx import ID_PASTE
        from wx import ID_SELECTALL

        super().__init__(sizedFrame=sizedFrame, menu=menu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        self.logger:          Logger  = getLogger(__name__)
        self._activeFrameId: FrameId = NO_FRAME_ID
        sizedFrame.Bind(EVT_MENU, self._onEditMenu, id=ID_UNDO)
        sizedFrame.Bind(EVT_MENU, self._onEditMenu, id=ID_REDO)
        sizedFrame.Bind(EVT_MENU, self._onEditMenu, id=ID_CUT)
        sizedFrame.Bind(EVT_MENU, self._onEditMenu, id=ID_COPY)
        sizedFrame.Bind(EVT_MENU, self._onEditMenu, id=ID_PASTE)
        sizedFrame.Bind(EVT_MENU, self._onEditMenu, id=ID_SELECTALL)

        self._appPubSubEngine.subscribe(messageType=MessageType.ACTIVE_DOCUMENT_CHANGED,
                                        uniqueId=EDIT_MENU_HANDLER_ID,
                                        listener=self._activeDocumentChangedListener
                                        )

    def _activeDocumentChangedListener(self, activeFrameId: FrameId):
        self.logger.info(f'{activeFrameId=}')
        self._activeFrameId = activeFrameId

    def _onEditMenu(self, event: CommandEvent):

        import wx       # So pattern matching works

        eventId: int = event.GetId()
        match eventId:

            case wx.ID_UNDO:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UNDO, frameId=self._activeFrameId)
            case wx.ID_REDO:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.REDO, frameId=self._activeFrameId)
            case wx.ID_CUT:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.CUT_SHAPES, frameId=self._activeFrameId)
            case wx.ID_COPY:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.COPY_SHAPES, frameId=self._activeFrameId)
            case wx.ID_PASTE:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.PASTE_SHAPES, frameId=self._activeFrameId)
            case wx.ID_PASTE:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.PASTE_SHAPES, frameId=self._activeFrameId)
            case wx.ID_SELECTALL:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.SELECT_ALL_SHAPES, frameId=self._activeFrameId)
            case _:
                self.logger.warning(f'Unknown event id {eventId}')

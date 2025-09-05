
from logging import Logger
from logging import getLogger

from wx import CommandEvent
from wx import EVT_MENU
from wx import ID_ABOUT

from wx import Menu

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from wx.lib.sized_controls import SizedFrame

from umldiagrammer.menuHandlers.BaseMenuHandler import BaseMenuHandler
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.dialogs.DlgAbout import DlgAbout

from umldiagrammer.UIIdentifiers import UIIdentifiers


class HelpMenuHandler(BaseMenuHandler):
    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        super().__init__(sizedFrame=sizedFrame, menu=menu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        sizedFrame.Bind(EVT_MENU, self._onDebugAppPubSub, id=UIIdentifiers.ID_MENU_HELP_PUB_SUB_ENGINE)
        sizedFrame.Bind(EVT_MENU, self._onAbout, id=ID_ABOUT)

    # noinspection PyUnusedLocal
    def _onAbout(self, event: CommandEvent):
        """
        Show the Pyut about dialog

        Args:
            event:
        """
        with DlgAbout(self._parent) as dlg:
            dlg.ShowModal()

    def _onDebugAppPubSub(self, event: CommandEvent):
        pass

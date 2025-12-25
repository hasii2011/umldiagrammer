from typing import List

from wx import Menu
from wx import MenuItem

from wx.lib.sized_controls import SizedFrame

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

class BaseMenuHandler:

    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self._menu:   Menu       = menu
        self._parent: SizedFrame = sizedFrame

        self._toggleableItems: List[MenuItem] = []

    def enableMenuItems(self):
        self._enableMenu(enable=True)

    def disableMenuItems(self):
        self._enableMenu(enable=False)

    def _enableMenu(self, enable: bool):
        for menuItem in self._toggleableItems:
            menuItem.Enable(enable=enable)

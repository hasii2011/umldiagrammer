
from wx import Menu
from wx import Window
from wx.lib.sized_controls import SizedFrame

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine


class BaseMenuHandler:

    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: UmlPubSubEngine):

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: UmlPubSubEngine  = umlPubSubEngine

        self._menu:   Menu       = menu
        self._parent: SizedFrame = sizedFrame

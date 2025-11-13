
from logging import Logger
from logging import getLogger
from typing import Dict
from typing import cast

from pubsub import pub

from wx import CommandEvent
from wx import EVT_MENU
from wx import ID_ABOUT

from wx import Menu

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from wx.lib.sized_controls import SizedFrame

from umldiagrammer.menuHandlers.BaseMenuHandler import BaseMenuHandler
from umldiagrammer.pubsubengine.AppPubSubEngine import AppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.dialogs.DlgAbout import DlgAbout

from umldiagrammer.UIIdentifiers import UIIdentifiers


class HelpMenuHandler(BaseMenuHandler):
    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        super().__init__(sizedFrame=sizedFrame, menu=menu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        sizedFrame.Bind(EVT_MENU, self._onDebugAppPubSub, id=UIIdentifiers.ID_MENU_HELP_PUB_SUB_ENGINE)
        sizedFrame.Bind(EVT_MENU, self._onAbout, id=ID_ABOUT)

        self._topicCount: Dict[str, int] = {}

    def setupPubSubTracing(self):
        appPubSubEngine: AppPubSubEngine = cast(AppPubSubEngine, self._appPubSubEngine)
        appPubSubEngine.debugSubscribeAllTopics(listener=self._snoop)

    # noinspection PyUnusedLocal
    def _onAbout(self, event: CommandEvent):
        """
        Show the Pyut about dialog

        Args:
            event:
        """
        with DlgAbout(self._parent) as dlg:
            dlg.ShowModal()

    # noinspection PyUnusedLocal
    def _onDebugAppPubSub(self, event: CommandEvent):
        from pprint import pformat

        gorgeousStr = pformat(self._topicCount, indent=4)

        # self.logger.info(f'\n{gorgeousStr}')
        print(f'\n{gorgeousStr}')

    # noinspection PyUnusedLocal
    def _snoop(self, opaqueTopicStr=pub.AUTO_TOPIC, **kwargs):
        # self.logger.info(f'Snooped on topic: {opaqueTopicStr} {kwargs}')
        from pubsub.core import Topic
        topic: Topic = cast(Topic, opaqueTopicStr)

        if opaqueTopicStr in self._topicCount.keys():
            self._topicCount[topic.getName()] += 1
        else:
            self._topicCount[topic.getName()] = 1

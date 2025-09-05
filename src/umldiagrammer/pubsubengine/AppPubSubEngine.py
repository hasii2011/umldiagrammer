
from typing import Callable

from logging import getLogger
from logging import Logger

from enum import Enum

from codeallybasic.BasePubSubEngine import BasePubSubEngine
from codeallybasic.BasePubSubEngine import Topic

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import UniqueId
from umldiagrammer.pubsubengine.MessageType import MessageType


class AppPubSubEngine(IAppPubSubEngine, BasePubSubEngine):

    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

    def subscribe(self, messageType: MessageType, uniqueId: UniqueId, callback: Callable):
        self._subscribe(topic=self._toTopic(messageType, uniqueId), listener=callback)

    def sendMessage(self, messageType: MessageType, uniqueId: UniqueId, **kwargs):
        self._sendMessage(topic=self._toTopic(messageType, uniqueId), **kwargs)

    def _toTopic(self, eventType: Enum, uniqueId: str) -> Topic:
        """
        TODO: use the code ally basic version when it becomes available
        Args:
            eventType:
            uniqueId:

        Returns:

        """
        topic: Topic = Topic(f'{eventType.value}.{uniqueId}')
        return topic

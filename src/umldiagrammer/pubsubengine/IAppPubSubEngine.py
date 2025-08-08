
from typing import Callable
from typing import NewType

from abc import ABC
from abc import abstractmethod

from umldiagrammer.pubsubengine.MessageType import MessageType

UniqueId = NewType('UniqueId', str)


class IAppPubSubEngine(ABC):

    @abstractmethod
    def subscribe(self, eventType: MessageType, uniqueId: UniqueId, callback: Callable):
        pass

    @abstractmethod
    def sendMessage(self, eventType: MessageType, uniqueId: UniqueId, **kwargs):
        pass

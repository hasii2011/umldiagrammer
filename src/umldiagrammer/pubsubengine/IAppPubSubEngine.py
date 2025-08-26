
from typing import Callable
from typing import List
from typing import NewType

from abc import ABC
from abc import abstractmethod

from umldiagrammer.pubsubengine.MessageType import MessageType

UniqueId  = NewType('UniqueId', str)
UniqueIds = NewType('UniqueIds', List[UniqueId])

class IAppPubSubEngine(ABC):

    @abstractmethod
    def subscribe(self, messageType: MessageType, uniqueId: UniqueId, callback: Callable):
        pass

    @abstractmethod
    def sendMessage(self, messageType: MessageType, uniqueId: UniqueId, **kwargs):
        pass

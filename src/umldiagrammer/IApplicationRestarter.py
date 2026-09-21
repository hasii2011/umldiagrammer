
from abc import ABC
from abc import abstractmethod


class IApplicationRestarter(ABC):
    """
    Interface for application restart mechanisms.
    """

    @classmethod
    @abstractmethod
    def restart(cls):
        """
        Replaces or restarts the running application process.
        """
        pass

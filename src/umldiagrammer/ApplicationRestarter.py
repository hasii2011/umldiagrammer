
from typing import List

# noinspection SpellCheckingInspection
from os import execv as osExecv

from sys import argv as sysArgv
from sys import modules as sysModules
from sys import executable as sysExecutable

from umldiagrammer.IApplicationRestarter import IApplicationRestarter


class ApplicationRestarter(IApplicationRestarter):
    """
    Replaces the current process image to restart the application.
    """

    @classmethod
    def restart(cls):
        """
        Replaces the current process image with a fresh Python process running
        the same executable and arguments.
        """
        args:     List[str]
        isFrozen: bool = getattr(sysModules['sys'], 'frozen', False)

        if isFrozen is True:
            args = [sysExecutable] + sysArgv[1:]
        else:
            args = [sysExecutable] + sysArgv

        osExecv(sysExecutable, args)

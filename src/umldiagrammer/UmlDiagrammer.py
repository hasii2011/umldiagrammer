
from typing import cast

from logging import Logger
from logging import getLogger

from wx import App

from umlshapes.lib.ogl import OGLInitialize

from codeallybasic.UnitTestBase import UnitTestBase

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umldiagrammer.UmlDiagrammerAppFrame import UmlDiagrammerAppFrame


class UmlDiagrammer(App):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._preferences:     UmlPreferences        = cast(UmlPreferences, None)
        self._wxFrame:         UmlDiagrammerAppFrame = cast(UmlDiagrammerAppFrame, None)

        # self._demoEventEngine = DemoEventEngine(listeningWindow=self._frame)    # Our app event engine

        super().__init__(redirect=False)    # This calls OnInit()

    def OnInit(self):
        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()
        self._preferences = UmlPreferences()
        self._wxFrame     = UmlDiagrammerAppFrame()

        self.SetTopWindow(self._wxFrame)

        return True


if __name__ == '__main__':

    UnitTestBase.setUpLogging()

    testApp: UmlDiagrammer = UmlDiagrammer()

    testApp.MainLoop()

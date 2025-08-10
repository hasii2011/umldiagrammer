
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

import logging.config

from os import sep as osSep

from json import load as jsonLoad

from codeallybasic.ResourceManager import ResourceManager
from wx import App

from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umldiagrammer.SystemMetrics import SystemMetrics
from umldiagrammer.Versions import Versions
from umldiagrammer.UmlDiagrammerAppFrame import UmlDiagrammerAppFrame


class UmlDiagrammer(App):

    JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"

    # noinspection SpellCheckingInspection
    PROJECT_NAME:           str = 'umldiagrammer'
    RESOURCES_PACKAGE_NAME: str = f'{PROJECT_NAME}.resources'
    RESOURCES_PATH:         str = f'{PROJECT_NAME}{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self):

        self._setupApplicationLogging()
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

    def MacOpenFiles(self, fileNames: List[str]):
        """
        Called in response to an "openFiles" Apple event.

        Args:
            fileNames:
        """
        self.logger.info(f'MacOpenFiles: {fileNames=}')
        #
        # appFrame:    PyutApplicationFrame = self._frame
        # self.logger.info(f'MacOpenFiles: {appFrame=}')
        # #
        # for fileName in fileNames:
        #     appFrame.loadByFilename(f'{fileName}')
        #     self.logger.info(f'Loaded: {fileNames=}')

    def _setupApplicationLogging(self):

        configFilePath: str = ResourceManager.retrieveResourcePath(bareFileName=UmlDiagrammer.JSON_LOGGING_CONFIG_FILENAME,
                                                                   resourcePath=UmlDiagrammer.RESOURCES_PATH,
                                                                   packageName=UmlDiagrammer.RESOURCES_PACKAGE_NAME)

        with open(configFilePath, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads   = False

    def displayVersionInformation(self):
        import platform

        version: Versions = Versions()
        print("Versions: ")
        print(f'Platform: {version.platform}')

        print(f'    System:       {platform.system()}')
        print(f'    Version:      {platform.version()}')
        print(f'    Release:      {platform.release()}')

        print(f'WxPython: {version.wxPythonVersion}')
        print(f'')
        print(f"UML Diagrammer:     {version.applicationVersion}")
        print(f'UML Diagrammer Packages')
        print(f'    Uml Shapes:      {version.umlShapesVersion}')
        print(f'    UML IO:          {version.umlioVersion}')

        print(f'')
        print(f'Python:   {version.pythonVersion}')

    def displaySystemMetrics(self):

        from wx import Size

        metrics: SystemMetrics = SystemMetrics()
        size:    Size           = metrics.screenResolution
        print('')
        print(f'Display Size: {metrics.displaySize}')
        print(f'x-DPI: {size.GetWidth()} y-DPI: {size.GetHeight()}')
        # print(f'{metrics.toolBarIconSize=}')

        # noinspection PyUnreachableCode
        if __debug__:
            self.logger.debug("Assertions are turned on")
        else:
            self.logger.debug("Assertions are turned off")


if __name__ == '__main__':

    umlDiagrammer: UmlDiagrammer = UmlDiagrammer()
    umlDiagrammer.displayVersionInformation()
    umlDiagrammer.displaySystemMetrics()

    umlDiagrammer.MainLoop()

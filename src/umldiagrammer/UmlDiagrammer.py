
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

import logging.config

from os import sep as osSep

from json import load as jsonLoad

from wx import App

from codeallybasic.ResourceManager import ResourceManager

from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umldiagrammer import START_STOP_MARKER
from umldiagrammer.DiagrammerTypes import MAIN_LOGGING_NAME
from umldiagrammer.SystemMetrics import SystemMetrics
from umldiagrammer.DependencyVersions import DependencyVersions
from umldiagrammer.UmlDiagrammerAppFrame import UmlDiagrammerAppFrame
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences


class UmlDiagrammer(App):

    JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"

    # noinspection SpellCheckingInspection
    PROJECT_NAME:           str = 'umldiagrammer'
    RESOURCES_PACKAGE_NAME: str = f'{PROJECT_NAME}.resources'
    RESOURCES_PATH:         str = f'{PROJECT_NAME}{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self):

        self._setupApplicationLogging()
        self.logger: Logger = getLogger(MAIN_LOGGING_NAME)

        self._umlPreferences:  UmlPreferences        = cast(UmlPreferences, None)
        self._preferences:     DiagrammerPreferences = DiagrammerPreferences()

        self._wxFrame:         UmlDiagrammerAppFrame = cast(UmlDiagrammerAppFrame, None)

        super().__init__(redirect=False)    # This calls OnInit()

    def OnInit(self):
        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()

        self._wxFrame = UmlDiagrammerAppFrame()

        self.SetTopWindow(self._wxFrame)

        if self._preferences.loadLastOpenedProject is True:
            self._wxFrame.loadLastOpenedProject()
        else:
            self._wxFrame.loadEmptyProject()

        return True

    def MacOpenFiles(self, fileNames: List[str]):
        """
        Called in response to an "openFiles" Apple event.

        Args:
            fileNames:
        """
        self.logger.info(f'MacOpenFiles: {fileNames=}')
        #
        appFrame: UmlDiagrammerAppFrame = self._wxFrame
        self.logger.debug(f'MacOpenFiles: {appFrame=}')
        #
        for fileName in fileNames:
            appFrame.loadProjectByFilename(fileName)

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

        version: DependencyVersions = DependencyVersions()
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
        print(f'Toolbar Icon Size: {metrics.toolBarIconSize}')

        if __debug__:
            self.logger.info("Assertions are turned on")
        else:
            self.logger.info("Assertions are turned off")


if __name__ == '__main__':

    umlDiagrammer: UmlDiagrammer = UmlDiagrammer()
    umlDiagrammer.logger.info(START_STOP_MARKER)

    umlDiagrammer.displayVersionInformation()
    umlDiagrammer.displaySystemMetrics()

    umlDiagrammer.MainLoop()


from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import EVT_MENU
from wx import FD_CHANGE_DIR
from wx import FD_FILE_MUST_EXIST
from wx import FD_OPEN
from wx import ID_OPEN
from wx import NB_LEFT

from wx import FileSelector
from wx import CallLater
from wx import CallAfter
from wx import CommandEvent
from wx import Notebook

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX

from umlio.Reader import Reader

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.UIIdentifiers import UIIdentifiers
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

PROJECT_WILDCARD: str = f'UML Diagrammer files (*.{PROJECT_SUFFIX})|*{PROJECT_SUFFIX}'
XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'

class FileMenuHandler:
    def __init__(self, sizedFrame: SizedFrame, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._sizedFrame: SizedFrame = sizedFrame

        self._openProjects: List[UmlProject] = []
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: UmlPubSubEngine  = umlPubSubEngine

        self._notebook:     Notebook = cast(Notebook, None)

        sizedFrame.Bind(EVT_MENU, self._onOpenProject, id=ID_OPEN)
        sizedFrame.Bind(EVT_MENU, self._onOpenXmlFile, id=UIIdentifiers.ID_FILE_MENU_OPEN_XML_PROJECT)

    # noinspection PyUnusedLocal
    def _onOpenProject(self, event: CommandEvent):

        selectedFile: str = FileSelector("Choose a project file to load", wildcard=PROJECT_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            self._loadProjectFile(Path(selectedFile))

    def _loadProjectFile(self, fileName: Path):
        reader: Reader = Reader()

        umlProject: UmlProject = reader.readProjectFile(fileName=fileName)
        self._loadNewProject(umlProject)

    # noinspection PyUnusedLocal
    def _onOpenXmlFile(self, event: CommandEvent):

        selectedFile: str = FileSelector("Choose a XML file to load", wildcard=XML_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            reader: Reader = Reader()
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(selectedFile))
            self.logger.debug(f'{umlProject=}')
            self._loadNewProject(umlProject)

    def _loadNewProject(self, umlProject: UmlProject):

        self._appPubSubEngine.sendMessage(eventType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, umlProject=umlProject)

        # if self._notebook is None:
        #     self._createTheOverArchingNotebook()
        #
        # projectPanel: UmlProjectPanel = UmlProjectPanel(self._notebook,
        #                                                 appPubSubEngine=self._appPubSubEngine,
        #                                                 umlPubSibEngine=self._umlPubSubEngine,
        #                                                 umlProject=umlProject
        #                                                 )
        # self._notebook.AddPage(page=projectPanel, text=umlProject.fileName.stem)
        # self._openProjects.append(umlProject)

    # def _createTheOverArchingNotebook(self):
    #     """
    #     Lazy UI creation
    #     """
    #     sizedPanel: SizedPanel = self._sizedFrame.GetContentsPane()
    #     sizedPanel.SetSizerProps(expand=True, proportion=1)
    #     sizedPanel.SetSizerType('vertical')
    #
    #     self._notebook = Notebook(sizedPanel, style=NB_LEFT)    # TODO: should be an application preference
    #     self._notebook.SetSizerProps(expand=True, proportion=1)
    #     CallLater(millis=200, callableObj=self._notebook.PostSizeEventToParent)
    #
    # # noinspection PyUnusedLocal
    # def onPageClosing(self, event):
    #     """
    #     Event handler that is called when a page in the notebook is closing
    #     """
    #     page = self._notebook.GetCurrentPage()
    #     page.Close()
    #     if len(self._openProjects) == 0:
    #         CallAfter(self._notebook.Destroy)
    #         self._notebook = None

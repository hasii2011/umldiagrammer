
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from umlio.Reader import Reader
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT

from wx import NB_LEFT
from wx import STB_DEFAULT_STYLE

from wx import ToolBar
from wx import Menu
from wx import MenuBar
from wx import Notebook

from wx import CallLater
from wx import CallAfter

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import UmlDocument
from umlio.IOTypes import UmlDocumentTitle
from umlio.IOTypes import UmlDocumentType

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.DiagrammerTypes import FrameIdMap
from umldiagrammer.UIMenuCreator import UIMenuCreator
from umldiagrammer.UmlProjectPanel import UmlProjectPanel
from umldiagrammer.menuHandlers.DiagrammerFileDropTarget import DiagrammerFileDropTarget

from umldiagrammer.pubsubengine.AppPubSubEngine import AppPubSubEngine
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType
from umldiagrammer.toolbar.ToolBarCreator import ToolBarCreator

DEFAULT_PROJECT_TITLE: UmlDocumentTitle = UmlDocumentTitle('NewDocument')           # TODO make a preference
DEFAULT_PROJECT_PATH:  Path             = Path('newProject.udt')

FRAME_WIDTH:  int = 800
FRAME_HEIGHT: int = 400

PROJECT_WILDCARD: str = f'UML Diagrammer files (*.{PROJECT_SUFFIX})|*{PROJECT_SUFFIX}'
XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'

ID_REFERENCE = NewType('ID_REFERENCE', int)


class UmlDiagrammerAppFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=None, title='UML Diagrammer', size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._notebook: Notebook = cast(Notebook, None)

        self._openProjects:    List[UmlProject] = []
        self._appPubSubEngine: IAppPubSubEngine = AppPubSubEngine()
        self._umlPubSubEngine: UmlPubSubEngine  = UmlPubSubEngine()

        self._createApplicationMenuBar()

        self.CreateStatusBar(style=STB_DEFAULT_STYLE)  # should always do this when there's a resize border
        self.SetAutoLayout(True)

        toolBarCreator: ToolBarCreator = ToolBarCreator(self)

        # self._tb:  ToolBar  = self.CreateToolBar(TB_HORIZONTAL | NO_BORDER | TB_FLAT)
        self._tb:  ToolBar  = toolBarCreator.toolBar

        self.SetToolBar(self._tb)
        self._tb.Realize()
        self.Show(True)

        self._preferences: UmlPreferences = UmlPreferences()
        self._appPubSubEngine.subscribe(eventType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, callback=self._loadProject)
        self._appPubSubEngine.subscribe(eventType=MessageType.NEW_PROJECT,  uniqueId=APPLICATION_FRAME_ID, callback=self._newProject)

        self._appPubSubEngine.subscribe(eventType=MessageType.FILES_DROPPED_ON_APPLICATION, uniqueId=APPLICATION_FRAME_ID, callback=self._onLoadDroppedFile)

        self._appPubSubEngine.subscribe(eventType=MessageType.UPDATE_APPLICATION_STATUS, uniqueId=APPLICATION_FRAME_ID, callback=self._onUpdateApplicationStatus)

        self.SetDropTarget(DiagrammerFileDropTarget(appPubSubEngine=self._appPubSubEngine, ))

    def _createApplicationMenuBar(self):

        uiMenuCreator: UIMenuCreator = UIMenuCreator(frame=self, appPubSubEngine=self._appPubSubEngine, umlPubSubEngine=self._umlPubSubEngine)
        uiMenuCreator.initializeMenus()

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = uiMenuCreator.fileMenu

        menuBar.Append(fileMenu, 'File')

        self.SetMenuBar(menuBar)

    def _newProject(self):
        if self._notebook is None:
            self._createTheApplicationNotebook()
            #
            # Create an empty project here
            #
            umlProject:  UmlProject  = UmlProject(DEFAULT_PROJECT_PATH)
            umlDocument: UmlDocument = UmlDocument(
                documentType=UmlDocumentType.CLASS_DOCUMENT,
                documentTitle=DEFAULT_PROJECT_TITLE
            )
            umlProject.umlDocuments[DEFAULT_PROJECT_TITLE] = umlDocument
            self._loadProject(umlProject=umlProject)

    def _loadProject(self, umlProject: UmlProject):

        if self._notebook is None:
            self._createTheApplicationNotebook()

        projectPanel: UmlProjectPanel = UmlProjectPanel(self._notebook,
                                                        appPubSubEngine=self._appPubSubEngine,
                                                        umlPubSibEngine=self._umlPubSubEngine,
                                                        umlProject=umlProject
                                                        )
        self._notebook.AddPage(page=projectPanel, text=umlProject.fileName.stem)
        self._openProjects.append(umlProject)

        frameIdMap: FrameIdMap = projectPanel.frameIdMap

        for frameId in frameIdMap.keys():
            self._umlPubSubEngine.subscribe(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                            frameId=frameId,
                                            callback=self._onUpdateApplicationStatus)

    def _createTheApplicationNotebook(self):
        """
        Lazy UI creation
        """
        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        sizedPanel.SetSizerType('vertical')

        self._notebook = Notebook(sizedPanel, style=NB_LEFT)    # TODO: should be an application preference
        self._notebook.SetSizerProps(expand=True, proportion=1)
        CallLater(millis=100, callableObj=self._notebook.PostSizeEventToParent)

    # noinspection PyUnusedLocal
    def _onPageClosing(self, event):
        """
        Event handler that is called when a page in the notebook is closing
        """
        page = self._notebook.GetCurrentPage()
        page.Close()
        if len(self._openProjects) == 0:
            CallAfter(self._notebook.Destroy)
            self._notebook = None

    def _onLoadDroppedFile(self, filename: str):
        """
        This is the handler for the FILES_DROPPED_ON_APPLICATION topic
        TODO: This is a slight duplicated of the code in the FileMenuHandler,
        can we keep it DRY?

        Args:
            filename:  Should end with either PROJECT_SUFFIX or XML_SUFFIX
        """

        fileNamePath: Path   = Path(filename)
        suffix:       str    = fileNamePath.suffix
        reader:       Reader = Reader()
        if suffix == XML_SUFFIX:
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(fileNamePath))
            self._loadProject(umlProject)

        elif suffix == PROJECT_SUFFIX:
            umlProject = reader.readProjectFile(fileName=fileNamePath)
            self._loadProject(umlProject)

        else:
            assert False, 'We should not get files with bad suffixes'

    def _onUpdateApplicationStatus(self, message: str):
        self.logger.warning(f'{message=}')
        self.SetStatusText(text=message)

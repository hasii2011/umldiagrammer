
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import EVT_MENU
from wx import FD_CHANGE_DIR
from wx import FD_FILE_MUST_EXIST
from wx import FD_OPEN
from wx import ID_OK
from wx import ID_OPEN
from wx import ID_PREFERENCES
from wx import ID_SAVE
from wx import ID_SAVEAS

from wx import FileSelector
from wx import CommandEvent
from wx import Notebook

from wx.lib.sized_controls import SizedFrame

from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX

from umlio.Reader import Reader

from umldiagrammer.dialogs.DlgPreferences import DlgPreferences
from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.UIIdentifiers import UIIdentifiers
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

PROJECT_WILDCARD: str = f'UML Diagrammer files (*.{PROJECT_SUFFIX})|*{PROJECT_SUFFIX}'
XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'

class FileMenuHandler:
    """
    In general the file menu handler can do the operations.  However, some are global in that
    the outer application frame controls the UI and this it must process some of these
    requests
    The public methods are used for the tool bar creator
    From the docs:
    The toolbar class emits menu commands in the same way that a frame menubar does, so you can use
    one EVT_MENU() macro for both a menu item and a toolbar button.

    """
    def __init__(self, sizedFrame: SizedFrame, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._sizedFrame: SizedFrame = sizedFrame

        self._openProjects: List[UmlProject] = []
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self._umlPubSubEngine: UmlPubSubEngine  = umlPubSubEngine

        self._notebook:     Notebook = cast(Notebook, None)

        sizedFrame.Bind(EVT_MENU, self.openProject,        id=ID_OPEN)
        sizedFrame.Bind(EVT_MENU, self.newProject,         id=UIIdentifiers.ID_FILE_MENU_NEW_PROJECT)
        sizedFrame.Bind(EVT_MENU, self.newClassDiagram,    id=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM)
        sizedFrame.Bind(EVT_MENU, self.newUseCaseDiagram,  id=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM)
        sizedFrame.Bind(EVT_MENU, self.newSequenceDiagram, id=UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM)

        sizedFrame.Bind(EVT_MENU, self.openXmlFile,    id=UIIdentifiers.ID_FILE_MENU_OPEN_XML_PROJECT)
        sizedFrame.Bind(EVT_MENU, self.fileSave,       id=ID_SAVE)
        sizedFrame.Bind(EVT_MENU, self._onFileSaveAs,  id=ID_SAVEAS)
        sizedFrame.Bind(EVT_MENU, self._onPreferences, id=ID_PREFERENCES)

    # noinspection PyUnusedLocal
    def openProject(self, event: CommandEvent):
        selectedFile: str = FileSelector("Choose a project file to load", wildcard=PROJECT_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            reader: Reader = Reader()

            umlProject: UmlProject = reader.readProjectFile(fileName=Path(selectedFile))
            self._loadNewProject(umlProject)

    # noinspection PyUnusedLocal
    def newProject(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.NEW_PROJECT, uniqueId=APPLICATION_FRAME_ID)

    def newClassDiagram(self, event: CommandEvent):
        pass

    def newUseCaseDiagram(self, event: CommandEvent):
        pass

    def newSequenceDiagram(self, event: CommandEvent):
        pass

    def fileSave(self, event: CommandEvent):
        pass

    # noinspection PyUnusedLocal
    def openXmlFile(self, event: CommandEvent):

        selectedFile: str = FileSelector("Choose a XML file to load", wildcard=XML_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            reader: Reader = Reader()
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(selectedFile))
            self.logger.debug(f'{umlProject=}')
            self._loadNewProject(umlProject)

    def _onFileSaveAs(self, event: CommandEvent):
        pass

    def _loadNewProject(self, umlProject: UmlProject):

        self._appPubSubEngine.sendMessage(messageType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, umlProject=umlProject)

    # noinspection PyUnusedLocal
    def _onPreferences(self, event: CommandEvent):

        with DlgPreferences(parent=self._sizedFrame, appPubSubEngine=self._appPubSubEngine) as dlg:
            if dlg.ShowModal() == ID_OK:
                self.logger.info(f'Got answer')
            else:
                self.logger.info(f'Cancelled')

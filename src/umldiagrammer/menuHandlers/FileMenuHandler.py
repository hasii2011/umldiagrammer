
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import OK
from wx import EVT_MENU
from wx import EVT_MENU_RANGE
from wx import FD_CHANGE_DIR
from wx import FD_FILE_MUST_EXIST
from wx import FD_OPEN
from wx import ICON_ERROR
from wx import ID_FILE1
from wx import ID_FILE9
from wx import ID_OK
from wx import ID_OPEN
from wx import ID_PREFERENCES
from wx import ID_SAVE
from wx import ID_SAVEAS

from wx import FileSelector
from wx import CommandEvent
from wx import Menu
from wx import MessageDialog
from wx import Notebook
from wx import FileHistory

from wx.lib.sized_controls import SizedFrame

from umlio.Reader import Reader

from umlio.IOTypes import UmlProject
from umlio.IOTypes import UmlDocumentType
from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import PROJECT_SUFFIX

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID
from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.dialogs.DlgPreferences import DlgPreferences

from umldiagrammer.UIIdentifiers import UIIdentifiers

from umldiagrammer.menuHandlers.BaseMenuHandler import BaseMenuHandler
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


PROJECT_WILDCARD: str = f'UML Diagrammer files (*.{PROJECT_SUFFIX})|*{PROJECT_SUFFIX}'
XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'

FileNames = NewType('FileNames', List[str])


class FileMenuHandler(BaseMenuHandler):
    """
    In general the file menu handler can do the operations.  However, some are global in that
    the outer application frame controls the UI and this it must process some of these
    requests
    The public methods are used for the tool bar creator
    From the docs:
    The toolbar class emits menu commands in the same way that a frame menu bar does, so you can use
    one EVT_MENU() macro for both a menu item and a toolbar button.

    """
    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        self.logger:       Logger                = getLogger(__name__)
        self._preferences: DiagrammerPreferences = DiagrammerPreferences()

        super().__init__(sizedFrame=sizedFrame, menu=menu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)
        self._sizedFrame: SizedFrame = sizedFrame

        self._openProjects: List[UmlProject] = []

        self._notebook:    Notebook    = cast(Notebook, None)
        self._fileHistory: FileHistory = cast(FileHistory, None)    # Must be injected

        sizedFrame.Bind(EVT_MENU, self.openProject,        id=ID_OPEN)
        sizedFrame.Bind(EVT_MENU, self.newProject,         id=UIIdentifiers.ID_FILE_MENU_NEW_PROJECT)
        sizedFrame.Bind(EVT_MENU, self.newClassDiagram,    id=UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM)
        sizedFrame.Bind(EVT_MENU, self.newUseCaseDiagram,  id=UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM)
        sizedFrame.Bind(EVT_MENU, self.newSequenceDiagram, id=UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM)

        sizedFrame.Bind(EVT_MENU, self.openXmlFile,    id=UIIdentifiers.ID_FILE_MENU_OPEN_XML_PROJECT)
        sizedFrame.Bind(EVT_MENU, self.fileSave,       id=ID_SAVE)
        sizedFrame.Bind(EVT_MENU, self._onFileSaveAs,  id=ID_SAVEAS)
        sizedFrame.Bind(EVT_MENU, self._closeProject,  id=UIIdentifiers.ID_MENU_FILE_PROJECT_CLOSE)
        sizedFrame.Bind(EVT_MENU, self._onPreferences, id=ID_PREFERENCES)

        sizedFrame.Bind(EVT_MENU_RANGE, self._onOpenRecent, id=ID_FILE1, id2=ID_FILE9)

    def _setFileHistory(self, fileHistory: FileHistory):
        self._fileHistory = fileHistory

    # noinspection PyTypeChecker
    fileHistory = property(fget=None, fset=_setFileHistory)

    # noinspection PyUnusedLocal
    def openProject(self, event: CommandEvent):
        selectedFile: str = FileSelector("Choose a project file to load", wildcard=PROJECT_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            reader: Reader = Reader()

            umlProject: UmlProject = reader.readProjectFile(fileName=Path(selectedFile))
            self._loadProject(umlProject)

    # noinspection PyUnusedLocal
    def newProject(self, event: CommandEvent):
        """
        Create an empty project
        """
        umlProject:  UmlProject  = UmlProject.emptyProject()
        self._loadProject(umlProject=umlProject)

    # noinspection PyUnusedLocal
    def newClassDiagram(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.CREATE_NEW_DIAGRAM, uniqueId=NOTEBOOK_ID, documentType=UmlDocumentType.CLASS_DOCUMENT)

    # noinspection PyUnusedLocal
    def newUseCaseDiagram(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.CREATE_NEW_DIAGRAM, uniqueId=NOTEBOOK_ID, documentType=UmlDocumentType.USE_CASE_DOCUMENT)

    # noinspection PyUnusedLocal
    def newSequenceDiagram(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.CREATE_NEW_DIAGRAM, uniqueId=NOTEBOOK_ID, documentType=UmlDocumentType.SEQUENCE_DOCUMENT)

    # noinspection PyUnusedLocal
    def fileSave(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.SAVE_PROJECT, uniqueId=APPLICATION_FRAME_ID)

    # noinspection PyUnusedLocal
    def openXmlFile(self, event: CommandEvent):

        selectedFile: str = FileSelector("Choose a XML file to load", wildcard=XML_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            reader: Reader = Reader()
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(selectedFile))
            self.logger.debug(f'{umlProject=}')
            self._loadProject(umlProject)

    # noinspection PyUnusedLocal
    def _onFileSaveAs(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.SAVE_AS_PROJECT, uniqueId=APPLICATION_FRAME_ID)

    # noinspection PyUnusedLocal
    def _closeProject(self, event: CommandEvent):
        self._appPubSubEngine.sendMessage(messageType=MessageType.CLOSE_PROJECT, uniqueId=NOTEBOOK_ID)

    def _loadProject(self, umlProject: UmlProject):
        self._appPubSubEngine.sendMessage(messageType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, umlProject=umlProject)

    # noinspection PyUnusedLocal
    def _onPreferences(self, event: CommandEvent):

        with DlgPreferences(parent=self._sizedFrame, appPubSubEngine=self._appPubSubEngine) as dlg:
            if dlg.ShowModal() == ID_OK:
                self.logger.info(f'Got answer')
            else:
                self.logger.info(f'Cancelled')

    def _onOpenRecent(self, event: CommandEvent):
        """
        Opens the selected 'recently' opened file
        Args:
            event:
        """
        assert self._fileHistory is not None, 'Developer forgot to inject file history handler'
        fileNum:  int = event.GetId() - ID_FILE1
        fileName: str = self._fileHistory.GetHistoryFile(fileNum)

        self.logger.info(f'{event=} - filename: {fileName}')
        reader: Reader = Reader()
        try:
            umlProject: UmlProject = reader.readProjectFile(fileName=Path(fileName))
            self._loadProject(umlProject)
        except FileNotFoundError:
            booBoo: MessageDialog = MessageDialog(parent=None, message='That project no longer exists', caption='Error', style=OK | ICON_ERROR)
            booBoo.ShowModal()

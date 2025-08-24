
from logging import Logger
from logging import getLogger

from wx import Frame
from wx import ID_EXIT
from wx import ID_OPEN
from wx import ID_PREFERENCES
from wx import ID_SAVE
from wx import ID_SAVEAS
from wx import Menu

from wx.lib.sized_controls import SizedFrame

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.menuHandlers.FileMenuHandler import FileMenuHandler
from umldiagrammer.UIIdentifiers import UIIdentifiers


class UIMenuCreator:
    def __init__(self, frame: SizedFrame, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)
        self._frame: Frame  = frame

        self._fileMenu: Menu = Menu()
        self._editMenu: Menu = Menu()
        self._toolMenu: Menu = Menu()
        self._helpMenu: Menu = Menu()

        self._fileMenuHandler: FileMenuHandler = FileMenuHandler(sizedFrame=frame, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

    @property
    def fileMenuHandler(self) -> FileMenuHandler:
        return self._fileMenuHandler

    def initializeMenus(self):

        self._initializeFileMenu()

    @property
    def fileMenu(self):
        return self._fileMenu

    def _initializeFileMenu(self):

        fileMenu: Menu = self._fileMenu

        self.mnuFileNew = Menu()

        self.mnuFileNew.Append(UIIdentifiers.ID_FILE_MENU_NEW_PROJECT,          '&New project\tCtrl-N', 'New project')
        self.mnuFileNew.Append(UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM,    'New c&lass diagram\tCtrl-L',    'New class diagram')
        self.mnuFileNew.Append(UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM, 'New s&equence diagram\tCtrl-E', 'New sequence diagram')
        self.mnuFileNew.Append(UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM,  "New &use-case diagram\tCtrl-U", 'New use-case diagram')

        fileMenu.AppendSubMenu(self.mnuFileNew, "&New")

        # Use stock identifier and properties
        fileMenu.Append(ID_OPEN)
        fileMenu.Append(UIIdentifiers.ID_FILE_MENU_OPEN_XML_PROJECT, 'Open XML Project', 'Open XML Project')
        fileMenu.Append(ID_SAVE)
        fileMenu.Append(ID_SAVEAS)
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_PROJECT_CLOSE,  "&Close project\tCtrl-W", "Close current project")
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_REMOVE_DIAGRAM, "&Delete diagram",        "Delete the diagram from the project")
        fileMenu.AppendSeparator()

        fileMenu.AppendSeparator()
        fileMenu.Append(ID_PREFERENCES, "P&references", "UML Diagrammer Preferences")
        fileMenu.AppendSeparator()
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_PRINT_SETUP,   "Print se&tup...", "Display the print setup dialog box")
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_PRINT_PREVIEW, "Print pre&view",  "Diagram preview before printing")
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_PRINT,         "&Print\tCtrl-P",  "Print the current diagram")
        fileMenu.AppendSeparator()
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_MANAGE_FILE_HISTORY, 'Manage Projects')
        fileMenu.AppendSeparator()

        fileMenu.Append(ID_EXIT, "E&xit", "Exit UML Diagrammer")

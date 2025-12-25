
from logging import Logger
from logging import getLogger

from wx import ID_ABOUT
from wx import ID_COPY
from wx import ID_CUT
from wx import ID_EXIT
from wx import ID_OPEN
from wx import ID_PASTE
from wx import ID_PREFERENCES
from wx import ID_REDO
from wx import ID_SAVE
from wx import ID_SAVEAS

from wx import Frame
from wx import ID_SELECTALL
from wx import ID_UNDO
from wx import Menu

from wx.lib.sized_controls import SizedFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umldiagrammer.menuHandlers.EditMenuHandler import EditMenuHandler
from umldiagrammer.menuHandlers.ExtensionsMenuHandler import ExtensionsMenuHandler
from umldiagrammer.menuHandlers.HelpMenuHandler import HelpMenuHandler
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.menuHandlers.FileMenuHandler import FileMenuHandler
from umldiagrammer.UIIdentifiers import UIIdentifiers


class UIMenuCreator:
    """
    For extensions the sub menu items are built in the menu handler instead of here
    """
    def __init__(self, frame: SizedFrame, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            frame:
            appPubSubEngine:
            umlPubSubEngine:
        """

        self.logger: Logger = getLogger(__name__)
        self._frame: Frame  = frame

        self._fileMenu:       Menu = Menu()
        self._editMenu:       Menu = Menu()
        self._extensionsMenu: Menu = Menu()
        self._helpMenu:       Menu = Menu()

        self._extensionsMenuHandler: ExtensionsMenuHandler = ExtensionsMenuHandler(
            sizedFrame=frame,
            menu=self._extensionsMenu,
            appPubSubEngine=appPubSubEngine,
            umlPubSubEngine=umlPubSubEngine
        )

        self._initializeMenus()
        self._fileMenuHandler: FileMenuHandler = FileMenuHandler(sizedFrame=frame, menu=self._fileMenu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)
        self._editMenuHandler: EditMenuHandler = EditMenuHandler(sizedFrame=frame, menu=self._editMenu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)
        self._helpMenuHandler: HelpMenuHandler = HelpMenuHandler(sizedFrame=frame, menu=self._helpMenu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

    @property
    def fileMenuHandler(self) -> FileMenuHandler:
        return self._fileMenuHandler

    @property
    def editMenuHandler(self) -> EditMenuHandler:
        return self._editMenuHandler

    @property
    def extensionsMenuHandler(self) -> ExtensionsMenuHandler:
        return self._extensionsMenuHandler

    @property
    def helpMenuHandler(self) -> HelpMenuHandler:
        return self._helpMenuHandler

    @property
    def fileMenu(self) -> Menu:
        return self._fileMenu

    @property
    def editMenu(self) -> Menu:
        return self._editMenu

    @property
    def extensionsMenu(self) -> Menu:
        return self._extensionsMenu

    @property
    def helpMenu(self) -> Menu:
        return self._helpMenu

    def enableMenus(self):
        self._fileMenuHandler.enableMenuItems()
        self._editMenuHandler.enableMenuItems()
        self._extensionsMenuHandler.enableMenuItems()

    def disableMenus(self):
        self._fileMenuHandler.disableMenuItems()
        self._editMenuHandler.disableMenuItems()
        self._extensionsMenuHandler.disableMenuItems()

    def _initializeMenus(self):
        self._initializeFileMenu()
        self._initializeEditMenu()
        self._initializeExtensionsMenu()
        self._initializeHelpMenu()

    def _initializeFileMenu(self):

        fileMenu: Menu = self._fileMenu

        self.mnuFileNew = Menu()

        self.mnuFileNew.Append(UIIdentifiers.ID_FILE_MENU_NEW_PROJECT,          '&New Project\tCtrl-N', 'New Project')
        self.mnuFileNew.Append(UIIdentifiers.ID_MENU_FILE_NEW_CLASS_DIAGRAM,    'New C&lass Diagram\tCtrl-L',    'New Class Diagram')
        # noinspection SpellCheckingInspection
        self.mnuFileNew.Append(UIIdentifiers.ID_MENU_FILE_NEW_SEQUENCE_DIAGRAM, 'New S&equence Diagram\tCtrl-E', 'New Sequence Diagram')
        self.mnuFileNew.Append(UIIdentifiers.ID_MENU_FILE_NEW_USECASE_DIAGRAM,  "New &Use Case Diagram\tCtrl-U", 'New Use Case Diagram')

        fileMenu.AppendSubMenu(self.mnuFileNew, "&New")

        # Use stock identifier and properties
        fileMenu.Append(ID_OPEN)
        fileMenu.Append(UIIdentifiers.ID_FILE_MENU_OPEN_XML_PROJECT, 'Open XML Project', 'Open XML Project')
        fileMenu.Append(ID_SAVE)
        fileMenu.Append(ID_SAVEAS)
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_PROJECT_CLOSE,  "&Close project\tCtrl-W", "Close current project")
        fileMenu.Append(UIIdentifiers.ID_MENU_FILE_DELETE_DIAGRAM, "&Delete diagram", "Delete the diagram from the project")
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

    def _initializeEditMenu(self):

        editMenu: Menu = self._editMenu

        editMenu.Append(ID_UNDO)
        editMenu.Append(ID_REDO)
        editMenu.AppendSeparator()
        #
        # Use all the stock properties
        #
        editMenu.Append(ID_CUT)
        editMenu.Append(ID_COPY)
        editMenu.Append(ID_PASTE)
        editMenu.AppendSeparator()
        editMenu.Append(ID_SELECTALL)
        editMenu.AppendSeparator()

    def _initializeExtensionsMenu(self):

        extensionsMenu: Menu = self._extensionsMenu
        self._extensionsMenuHandler.initializeSubMenus(extensionsMenu=extensionsMenu)

    def _initializeHelpMenu(self):

        helpMenu: Menu = self._helpMenu

        helpMenu.Append(UIIdentifiers.ID_MENU_HELP_PUB_SUB_ENGINE, 'Debug App Pub Sub', 'Pub Sub Engine Diagnostics')
        helpMenu.Append(ID_ABOUT, '&About', 'Uml Diagrammer Information')

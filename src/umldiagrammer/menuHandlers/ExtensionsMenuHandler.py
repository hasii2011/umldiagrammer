
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from umlextensions.ExtensionsPubSub import ExtensionsPubSub
from wx import EVT_MENU

from wx import Menu
from wx import CommandEvent

from wx.lib.sized_controls import SizedFrame

from umlextensions.ExtensionsManager import ExtensionDetails
from umlextensions.ExtensionsManager import InputExtensionMap
from umlextensions.ExtensionsManager import WindowId
from umlextensions.ExtensionsManager import ToolExtensionMap

from umlextensions.input.BaseInputExtension import BaseInputExtension

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlextensions.ExtensionsManager import ExtensionsManager

from umldiagrammer.UmlExtensionsFacade import UmlExtensionsFacade
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.menuHandlers.BaseMenuHandler import BaseMenuHandler


class ExtensionsMenuHandler(BaseMenuHandler):
    """
    This particular handler will build the sub menus since it needs the extensions manager
    to determine what those should be
    """
    def __init__(self, sizedFrame: SizedFrame, menu: Menu, appPubSubEngine: IAppPubSubEngine, umlPubSubEngine: IUmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        super().__init__(sizedFrame=sizedFrame, menu=menu, appPubSubEngine=appPubSubEngine, umlPubSubEngine=umlPubSubEngine)

        extensionsFacade: UmlExtensionsFacade = UmlExtensionsFacade()
        extensionsFacade.umlPubSub = umlPubSubEngine

        self._extensionManager: ExtensionsManager = ExtensionsManager(umlPubSubEngine=umlPubSubEngine,
                                                                      extensionsFacade=extensionsFacade
                                                                      )

    @property
    def extensionsPubSub(self) -> ExtensionsPubSub:
        return self._extensionManager.extensionsPubSub

    def _onImport(self, event: CommandEvent):
        wxId:          int           = event.GetId()
        extensionsDetails: ExtensionDetails = self._extensionManager.doImport(wxId=cast(WindowId, wxId))
        self.logger.info(f'Import: {extensionsDetails=}')

    def _onToolAction(self, event: CommandEvent):
        wxId:          int           = event.GetId()
        extensionsDetails: ExtensionDetails = self._extensionManager.doToolAction(wxId=cast(WindowId, wxId))
        self.logger.info(f'Import: {extensionsDetails=}')

    def initializeSubMenus(self, extensionsMenu: Menu):
        pass

        inputSubMenu:  Menu = self._initializeInputSubMenu()
        outputSubMenu: Menu = self._initializeOutputSubMenu()
        toolsSubMenu:  Menu = self._initializeToolSubMenu()
        #
        extensionsMenu.AppendSubMenu(inputSubMenu,  'Input')
        extensionsMenu.AppendSubMenu(outputSubMenu, 'Output')
        extensionsMenu.AppendSubMenu(toolsSubMenu,  'Tools')

    def _initializeInputSubMenu(self) -> Menu:
        """
        Returns: The import submenu.
        """
        subMenu: Menu = Menu()

        inputExtensionsMap: InputExtensionMap = self._extensionManager.inputExtensionsMap

        for wxId in inputExtensionsMap.extensionIdMap.keys():
            clazz:          type = inputExtensionsMap.extensionIdMap[wxId]
            extensionInstance: BaseInputExtension = clazz(None)

            pluginName: str = extensionInstance.inputFormat.formatName

            subMenu = self._makeSubMenuEntry(subMenu=subMenu, wxId=wxId, pluginName=pluginName, callback=self._onImport)

        return subMenu

    def _initializeOutputSubMenu(self) -> Menu:
        subMenu: Menu = Menu()
        return subMenu

    def _initializeToolSubMenu(self) -> Menu:
        subMenu: Menu = Menu()

        toolExtensionsMap: ToolExtensionMap = self._extensionManager.toolExtensionsMap

        for wxId in toolExtensionsMap.extensionIdMap.keys():
            clazz:        type = toolExtensionsMap.extensionIdMap[wxId]
            toolInstance: BaseInputExtension = clazz(None)

            toolName: str = toolInstance.name
            subMenu = self._makeSubMenuEntry(subMenu=subMenu, wxId=wxId, pluginName=toolName, callback=self._onToolAction)

        return subMenu

    def _makeSubMenuEntry(self, subMenu: Menu, wxId: int, pluginName: str, callback: Callable) -> Menu:

        subMenu.Append(wxId, pluginName)
        self._parent.Bind(EVT_MENU, callback, id=wxId)

        return subMenu

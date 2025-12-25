
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

        inputSubMenu:  Menu = self._initializeInputMenu()
        outputSubMenu: Menu = self._initializeOutputMenu()
        toolsSubMenu:  Menu = self._initializeTool()
        #
        extensionsMenu.AppendSubMenu(inputSubMenu,  'Input')
        extensionsMenu.AppendSubMenu(outputSubMenu, 'Output')
        extensionsMenu.AppendSubMenu(toolsSubMenu,  'Tools')

        inputItems  = inputSubMenu.GetMenuItems()
        outputItems = outputSubMenu.GetMenuItems()
        toolItems   = toolsSubMenu.GetMenuItems()

        for itm in inputItems:
            self._toggleableItems.append(itm)

        for itm in outputItems:
            self._toggleableItems.append(itm)

        for itm in toolItems:
            self._toggleableItems.append(itm)

    def _initializeInputMenu(self) -> Menu:
        """
        Returns: The import submenu.
        """
        menu: Menu = Menu()

        inputExtensionsMap: InputExtensionMap = self._extensionManager.inputExtensionsMap

        for wxId in inputExtensionsMap.extensionIdMap.keys():
            clazz:          type = inputExtensionsMap.extensionIdMap[wxId]
            extensionInstance: BaseInputExtension = clazz(None)

            pluginName: str = extensionInstance.inputFormat.formatName

            menu = self._makeSubMenuEntry(subMenu=menu, wxId=wxId, pluginName=pluginName, callback=self._onImport)

        return menu

    def _initializeOutputMenu(self) -> Menu:
        menu: Menu = Menu()
        return menu

    def _initializeTool(self) -> Menu:
        menu: Menu = Menu()

        toolExtensionsMap: ToolExtensionMap = self._extensionManager.toolExtensionsMap

        for wxId in toolExtensionsMap.extensionIdMap.keys():
            clazz:        type = toolExtensionsMap.extensionIdMap[wxId]
            toolInstance: BaseInputExtension = clazz(None)

            toolName: str = toolInstance.name
            menu = self._makeSubMenuEntry(subMenu=menu, wxId=wxId, pluginName=toolName, callback=self._onToolAction)

        return menu

    def _makeSubMenuEntry(self, subMenu: Menu, wxId: int, pluginName: str, callback: Callable) -> Menu:

        subMenu.Append(wxId, pluginName)
        self._parent.Bind(EVT_MENU, callback, id=wxId)

        return subMenu


from typing import cast

from wx import BORDER_THEME
from wx import EVT_CHECKBOX

from wx import CheckBox
from wx import CommandEvent
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.PositionControl import PositionControl

from umldiagrammer.dialogs.BasePreferencesPanel import BasePreferencesPanel
from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


class StartupPreferencesPanel(BasePreferencesPanel):
    """
    Implemented using sized components for better platform look and feel
    """

    def __init__(self, parent: Window, appPubSubEngine: IAppPubSubEngine):

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        super().__init__(parent, style=BORDER_THEME)
        self.SetSizerType('vertical')

        self._cbCenterAppOnStartup:   CheckBox          = cast(CheckBox, None)
        self._appPositionControls:    PositionControl   = cast(PositionControl, None)
        self._cbFullScreenOnStartup:  CheckBox          = cast(CheckBox, None)
        self._appDimensionsContainer: DimensionsControl = cast(DimensionsControl, None)

        self._layoutControls(parent)

        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=3)

    def _layoutControls(self, parent):

        self._cbCenterAppOnStartup = CheckBox(self, label='Center on Startup')
        self._appPositionControls  = self._layoutAppPositionControls(sizedPanel=self)

        self._cbFullScreenOnStartup  = CheckBox(self, label='Full Screen on Startup')
        self._appDimensionsContainer = self._layoutAppSizeControls(sizedPanel=self)

        self._setControlValues()
        parent.Bind(EVT_CHECKBOX, self._onCenterOnStartupChanged,    self._cbCenterAppOnStartup)
        parent.Bind(EVT_CHECKBOX, self._onFullScreenOnStartupChange, self._cbFullScreenOnStartup)

    @property
    def name(self) -> str:
        return 'Positions'

    def _layoutAppPositionControls(self, sizedPanel: SizedPanel) -> PositionControl:

        appPositionControls: PositionControl = PositionControl(sizedPanel=sizedPanel, displayText='Startup Position',
                                                               minValue=0, maxValue=2048,
                                                               valueChangedCallback=self._appPositionChanged,
                                                               setControlsSize=True)

        appPositionControls.SetSizerProps(expand=True, proportion=1)
        return appPositionControls

    def _layoutAppSizeControls(self, sizedPanel: SizedPanel) -> DimensionsControl:

        appSizeControls: DimensionsControl = DimensionsControl(sizedPanel=sizedPanel, displayText="Startup Width/Height",
                                                               minValue=480, maxValue=4096,
                                                               valueChangedCallback=self._appSizeChanged,
                                                               setControlsSize=True)

        appSizeControls.SetSizerProps(expand=True, proportion=1)
        return appSizeControls

    def _setControlValues(self):
        """
        Set the position controls based on the value of appropriate preference value
        """
        if self._preferences.centerAppOnStartup is True:
            self._appPositionControls.enableControls(False)
            self._cbCenterAppOnStartup.SetValue(True)
        else:
            self._appPositionControls.enableControls(True)
            self._cbCenterAppOnStartup.SetValue(False)

        if self._preferences.fullScreen is True:
            self._appDimensionsContainer.enableControls(False)
            self._cbFullScreenOnStartup.SetValue(True)
        else:
            self._appDimensionsContainer.enableControls(True)
            self._cbFullScreenOnStartup.SetValue(False)

        self._appDimensionsContainer.dimensions = self._preferences.startupSize
        self._appPositionControls.position      = self._preferences.startupPosition

    def _enablePositionControls(self, enable: bool):
        """
        Enable/Disable position controls based on the value of appropriate preference value

        Args:
            enable:  If 'True' the position controls are disabled else they are enabled
        """
        if enable is True:
            self._appPositionControls.enableControls(False)
        else:
            self._appPositionControls.enableControls(True)

    def _appPositionChanged(self, newValue: Position):
        self._preferences.startupPosition = newValue
        self._appPubSubEngine.sendMessage(MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID, override=True)

    def _appSizeChanged(self, newValue: Dimensions):
        self._preferences.startupSize = newValue

        self._appPubSubEngine.sendMessage(MessageType.OVERRIDE_PROGRAM_EXIT_SIZE, uniqueId=APPLICATION_FRAME_ID, override=True)

    def _onCenterOnStartupChanged(self, event: CommandEvent):
        """
        """
        newValue: bool = event.IsChecked()

        self._preferences.centerAppOnStartup = newValue
        self._enablePositionControls(newValue)
        if newValue is True:
            self._appPubSubEngine.sendMessage(MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID)

    def _onFullScreenOnStartupChange(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.fullScreen = newValue
        if newValue is True:
            self._appPubSubEngine.sendMessage(MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID)


from typing import cast

from wx import EVT_CHECKBOX

from wx import CheckBox
from wx import CommandEvent
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsParameters
from codeallyadvanced.ui.widgets.PositionControl import PositionControl
from codeallyadvanced.ui.widgets.PositionControl import PositionParameters

from umldiagrammer.dialogs.BasePreferencesPanel import BasePreferencesPanel
from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

POSITION_MIN_VALUE: int = 0
POSITION_MAX_VALUE: int = 2048

SIZE_MIN_VALUE: int = 480
SIZE_MAX_VALUE: int = 4096


class StartupPreferencesPanel(BasePreferencesPanel):
    """
    Implemented using sized components for better platform look and feel
    """
    def __init__(self, parent: Window, appPubSubEngine: IAppPubSubEngine):

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        super().__init__(parent)
        self.SetSizerType('vertical')

        self._cbCenterAppOnStartup:   CheckBox          = cast(CheckBox, None)
        self._appPositionControls:    PositionControl   = cast(PositionControl, None)
        self._cbFullScreenOnStartup:  CheckBox          = cast(CheckBox, None)
        self._appSizeControls:        DimensionsControl = cast(DimensionsControl, None)

        self._layoutControls(parent)

    def _layoutControls(self, parent):

        self._appPositionControls = self._layoutAppPositionControls(sizedPanel=self)
        self._appSizeControls     = self._layoutAppSizeControls(sizedPanel=self)

        self._setControlValues()
        parent.Bind(EVT_CHECKBOX, self._onCenterOnStartupChanged,    self._cbCenterAppOnStartup)
        parent.Bind(EVT_CHECKBOX, self._onFullScreenOnStartupChange, self._cbFullScreenOnStartup)

    @property
    def name(self) -> str:
        return 'Startup'

    def _layoutAppPositionControls(self, sizedPanel: SizedPanel) -> PositionControl:

        self._cbCenterAppOnStartup = CheckBox(sizedPanel, label='Center on Startup')

        positionParameters: PositionParameters = PositionParameters(
            caption='Startup Position',
            minValue=POSITION_MIN_VALUE,
            maxValue=POSITION_MAX_VALUE,
            valueChangedCallback=self._appPositionChanged
        )
        appPositionControls: PositionControl = PositionControl(parent=sizedPanel, parameters=positionParameters)

        return appPositionControls

    def _layoutAppSizeControls(self, sizedPanel: SizedPanel) -> DimensionsControl:

        self._cbFullScreenOnStartup = CheckBox(sizedPanel, label='Full Screen on Startup')

        dimensionsParameters: DimensionsParameters = DimensionsParameters(
            caption='Startup Width/Height',
            minValue=SIZE_MIN_VALUE,
            maxValue=SIZE_MAX_VALUE,
            valueChangedCallback=self._appSizeChanged
        )
        appSizeControls: DimensionsControl = DimensionsControl(parent=sizedPanel, parameters=dimensionsParameters)

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
            self._appSizeControls.enableControls(False)
            self._cbFullScreenOnStartup.SetValue(True)
        else:
            self._appSizeControls.enableControls(True)
            self._cbFullScreenOnStartup.SetValue(False)

        self._appSizeControls.dimensions = self._preferences.startupSize
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
        self._appSizeControls.enableControls(not newValue)
        if newValue is True:
            self._appPubSubEngine.sendMessage(MessageType.OVERRIDE_PROGRAM_EXIT_POSITION, uniqueId=APPLICATION_FRAME_ID)

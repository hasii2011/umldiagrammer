
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from pathlib import Path

from wx import EVT_CHECKBOX
from wx import EVT_RADIOBOX
from wx import ID_ANY

from wx import CheckBox
from wx import CommandEvent
from wx import RA_SPECIFY_ROWS
from wx import RadioBox
from wx import Window

from wx import NewIdRef as wxNewIdRef


from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DirectorySelector import DirectorySelector

from umldiagrammer.dialogs.BasePreferencesPanel import BasePreferencesPanel
from umldiagrammer.dialogs.StartupPreferencesPanel import StartupPreferencesPanel
from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences
from umldiagrammer.preferences.FileHistoryPreference import FileHistoryPreference
from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize


# from pyut.resources.img import folder as ImgFolder


@dataclass
class ControlData:
    label:        str      = ''
    initialValue: bool     = False
    instanceVar:  CheckBox = cast(CheckBox, None)
    wxId:         int      = 0


class GeneralPreferencesPanel(BasePreferencesPanel):
    """
    Implemented using sized components for better platform look and feel
    Since these are a bunch of checkboxes that drive true/false preferences,
    I can encapsulate creating them in a list with a dataclass that hosts all
    the necessary creation information;  How esoteric of me !!!  ;-(
    """
    AUTO_RESIZE_ID:               int = wxNewIdRef()
    TOOLBAR_ICON_SIZE_ID:         int = wxNewIdRef()
    LOAD_LAST_OPENED_PROJECT_ID:  int = wxNewIdRef()

    def __init__(self, parent: Window, appPubSubEngine: IAppPubSubEngine):
        super().__init__(parent)

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine
        self.SetSizerType('vertical')

        self.logger:  Logger = getLogger(__name__)
        self._change: bool   = False

        self._fileHistoryPathPref: RadioBox          = cast(RadioBox, None)
        self._directorySelector:   DirectorySelector = cast(DirectorySelector, None)

        p: DiagrammerPreferences = self._preferences
        self._controlData = [
            # ControlData(label='&Full Screen on startup',   initialValue=p.fullScreen,             wxId=GeneralPreferencesPanel.MAXIMIZE_ID),
            ControlData(label='&Resize classes on edit',   initialValue=p.autoResizeShapesOnEdit, wxId=GeneralPreferencesPanel.AUTO_RESIZE_ID),
            ControlData(label='&Large Toolbar Icons',      initialValue=self._isLargeIconSize(),  wxId=GeneralPreferencesPanel.TOOLBAR_ICON_SIZE_ID),
            ControlData(label='Load Last &Opened Project', initialValue=p.loadLastOpenedProject,  wxId=GeneralPreferencesPanel.LOAD_LAST_OPENED_PROJECT_ID),
        ]

        self._layoutWindow(sizedPanel=self)

        self._setControlValues()

        self.Bind(EVT_RADIOBOX, self._onFileHistoryPathPrefChanged, self._fileHistoryPathPref)

    def _layoutWindow(self, sizedPanel: SizedPanel):

        self._layoutTrueFalsePreferences(sizedPanel)
        StartupPreferencesPanel(parent=sizedPanel, appPubSubEngine=self._appPubSubEngine)
        self._layoutDiagramsDirectory(sizedPanel)
        self._layoutFileHistoryPreferenceControl(sizedPanel)

        # self._fixPanelSize(panel=self)

    @property
    def name(self) -> str:
        return 'General'

    def _layoutTrueFalsePreferences(self, parentPanel: SizedPanel):
        """
        I represent this in the UI with a CheckBox
        Args:
            parentPanel:
        """
        trueFalsePanel: SizedStaticBox = SizedStaticBox(parentPanel, label='')
        trueFalsePanel.SetSizerType('Vertical')
        trueFalsePanel.SetSizerProps(expand=True, proportion=1)

        for cd in self._controlData:
            control: ControlData = cast(ControlData, cd)
            control.instanceVar = CheckBox(trueFalsePanel, id=control.wxId, label=control.label)
            control.instanceVar.SetValue(control.initialValue)
            parentPanel.Bind(EVT_CHECKBOX, self._onTrueFalsePreferenceChanged, control.instanceVar)

    def _layoutDiagramsDirectory(self, sizedPanel: SizedPanel):

        dsPanel: SizedStaticBox = SizedStaticBox(sizedPanel, label='Diagrams Directory ')
        dsPanel.SetSizerProps(expand=True, proportion=1)

        self._directorySelector = DirectorySelector(parent=dsPanel, pathChangedCallback=self._pathChangedCallback)
        self._directorySelector.SetSizerProps(expand=True, proportion=1)

    def _layoutFileHistoryPreferenceControl(self, parentPanel: SizedPanel):

        options: List[str] = [
            FileHistoryPreference.SHOW_NEVER.value,
            FileHistoryPreference.SHOW_ALWAYS.value,
            FileHistoryPreference.SHOW_IF_DIFFERENT.value
        ]

        rb: RadioBox = RadioBox(parent=parentPanel,
                                id=ID_ANY,
                                label='File History Path Style',
                                choices=options,
                                majorDimension=1,
                                style=RA_SPECIFY_ROWS)

        self._fileHistoryPathPref = rb

    def _setControlValues(self):
        """

        """
        self._directorySelector.directoryPath = self._preferences.diagramsDirectory

        chosen: str = self._preferences.fileHistoryDisplay.value
        idx:    int = self._fileHistoryPathPref.FindString(chosen)

        self._fileHistoryPathPref.SetSelection(idx)

    def _onTrueFalsePreferenceChanged(self, event: CommandEvent):

        eventID:  int = event.GetId()
        newValue: bool = event.IsChecked()

        p: DiagrammerPreferences = self._preferences

        match eventID:
            case GeneralPreferencesPanel.AUTO_RESIZE_ID:
                p.autoResizeShapesOnEdit = newValue
            case GeneralPreferencesPanel.TOOLBAR_ICON_SIZE_ID:
                # noinspection PySimplifyBooleanCheck
                if newValue is True:
                    p.toolBarIconSize = ToolBarIconSize.LARGE
                else:
                    p.toolBarIconSize = ToolBarIconSize.SMALL
            case GeneralPreferencesPanel.LOAD_LAST_OPENED_PROJECT_ID:
                p.loadLastOpenedProject = newValue

        self._changed = True

    # noinspection PyUnusedLocal
    def _onResetTips(self, event: CommandEvent):
        self._preferences.currentTip = 0

    def _onFileHistoryPathPrefChanged(self, event: CommandEvent):

        newValue: str = event.GetString()
        self.logger.info(f'File History Path Preferences changed.  {newValue=}')
        newPreference: FileHistoryPreference = FileHistoryPreference(newValue)
        self._preferences.fileHistoryDisplay = newPreference

    def _pathChangedCallback(self, newPath: Path):
        self._preferences.diagramsDirectory = str(newPath)

    def _isLargeIconSize(self) -> bool:
        if self._preferences.toolBarIconSize == ToolBarIconSize.LARGE:
            return True
        else:
            return False

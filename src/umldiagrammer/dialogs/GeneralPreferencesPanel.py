
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from pathlib import Path

from wx import ID_ANY
from wx import EVT_CHOICE
from wx import BORDER_THEME
from wx import EVT_CHECKBOX
from wx import EVT_RADIOBOX
from wx import RA_SPECIFY_COLS

from wx import Choice
from wx import CheckBox
from wx import RadioBox
from wx import Window
from wx import CommandEvent

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DirectorySelector import DirectorySelector

from umldiagrammer.dialogs.BasePreferencesPanel import BasePreferencesPanel

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences
from umldiagrammer.preferences.ProjectTabPosition import ProjectTabPosition
from umldiagrammer.preferences.ProjectHistoryDisplayType import ProjectHistoryDisplayType

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine

from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize
from umldiagrammer.toolbar.ToolBarPosition import ToolBarPosition


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

        self._projectHistoryPathPref: RadioBox          = cast(RadioBox, None)
        self._toolBarIconSizePref:    RadioBox          = cast(RadioBox, None)
        self._directorySelector:      DirectorySelector = cast(DirectorySelector, None)
        self._toolBarPosition:        Choice            = cast(Choice, None)
        self._projectTabPosition:     Choice            = cast(Choice, None)

        p: DiagrammerPreferences = self._preferences
        self._controlData = [
            # ControlData(label='&Full Screen on startup',   initialValue=p.fullScreen,             wxId=GeneralPreferencesPanel.MAXIMIZE_ID),
            ControlData(label='&Resize classes on edit',   initialValue=p.autoResizeShapesOnEdit, wxId=GeneralPreferencesPanel.AUTO_RESIZE_ID),
            ControlData(label='Load Last &Opened Project', initialValue=p.loadLastOpenedProject,  wxId=GeneralPreferencesPanel.LOAD_LAST_OPENED_PROJECT_ID),
        ]

        self._layoutWindow(sizedPanel=self)

        self._setControlValues()

        self.Bind(EVT_RADIOBOX, self._onFileHistoryPathPrefChanged,     self._projectHistoryPathPref)
        self.Bind(EVT_RADIOBOX, self._onToolBarIconSizePrefChanged,     self._toolBarIconSizePref)
        self.Bind(EVT_CHOICE,   self._onToolBarPositionValueChanged,    self._toolBarPosition)
        self.Bind(EVT_CHOICE,   self._onProjectTabPositionValueChanged, self._projectTabPosition)

    @property
    def name(self) -> str:
        return 'General'

    def _layoutWindow(self, sizedPanel: SizedPanel):

        self._layoutTrueFalsePreferences(sizedPanel)
        self._layoutDiagramsDirectory(sizedPanel)

        rbPanel: SizedStaticBox = SizedStaticBox(sizedPanel, label='', style=BORDER_THEME)
        rbPanel.SetSizerProps(expand=True, proportion=2)
        rbPanel.SetSizerType('horizontal')

        self._layoutToolBarIconSize(rbPanel)

        self._layoutDiagrammerElementsPositions(sizedPanel)
        self._layoutProjectHistoryDisplayPreferenceControl(sizedPanel)

        self._fixPanelSize(panel=self)

    def _layoutTrueFalsePreferences(self, parentPanel: SizedPanel):
        """
        I represent this in the UI with a CheckBox
        Args:
            parentPanel:
        """
        trueFalsePanel: SizedStaticBox = SizedStaticBox(parentPanel, label='')

        for cd in self._controlData:
            control: ControlData = cd
            control.instanceVar = CheckBox(trueFalsePanel, id=control.wxId, label=control.label)
            control.instanceVar.SetValue(control.initialValue)
            parentPanel.Bind(EVT_CHECKBOX, self._onTrueFalsePreferenceChanged, control.instanceVar)

        trueFalsePanel.SetSizerType('Vertical')
        trueFalsePanel.SetSizerProps(expand=True, proportion=1)

    def _layoutDiagramsDirectory(self, sizedPanel: SizedPanel):

        dsPanel: SizedStaticBox = SizedStaticBox(sizedPanel, label='Diagrams Directory ', style=BORDER_THEME)
        dsPanel.SetSizerProps(expand=True, proportion=1)

        self._directorySelector = DirectorySelector(parent=dsPanel, pathChangedCallback=self._pathChangedCallback)
        self._directorySelector.SetSizerProps(expand=True, proportion=1)

    def _layoutProjectHistoryDisplayPreferenceControl(self, parentPanel: SizedPanel):

        options: List[str] = [
            ProjectHistoryDisplayType.SHOW_NEVER.value,
            ProjectHistoryDisplayType.SHOW_ALWAYS.value,
            ProjectHistoryDisplayType.SHOW_IF_DIFFERENT.value
        ]

        rb: RadioBox = RadioBox(parent=parentPanel,
                                id=ID_ANY,
                                label='Project History Path Style',
                                choices=options,
                                majorDimension=1,
                                style=RA_SPECIFY_COLS | BORDER_THEME)

        rb.SetSizerProps(expand=True, proportion=1)

        self._projectHistoryPathPref = rb

    def _layoutToolBarIconSize(self, parentPanel: SizedStaticBox):

        options: List[str] = [
            ToolBarIconSize.SMALL.value,
            ToolBarIconSize.MEDIUM.value,
            ToolBarIconSize.LARGE.value,
            ToolBarIconSize.EXTRA_LARGE.value,
        ]

        rb: RadioBox = RadioBox(parent=parentPanel,
                                id=ID_ANY,
                                label='Toolbar Icon Size',
                                choices=options,
                                majorDimension=1,
                                style=RA_SPECIFY_COLS | BORDER_THEME)

        rb.SetSizerProps(expand=True, proportion=1)

        self._toolBarIconSizePref = rb

    def _layoutDiagrammerElementsPositions(self, sizedPanel: SizedPanel):

        positionPanel: SizedPanel = SizedPanel(parent=sizedPanel)
        positionPanel.SetSizerType('horizontal')
        positionPanel.SetSizerProps(expand=True, proportion=1)

        toolBarPositions: List[str] = [s.value for s in ToolBarPosition]
        del toolBarPositions[-1]        # Assumes last item is the "NOT_SET" marker

        toolBarPositionSSB: SizedStaticBox = SizedStaticBox(positionPanel, label='Toolbar Position', style=BORDER_THEME)
        toolBarPositionSSB.SetSizerProps(expand=True, proportion=1)

        self._toolBarPosition = Choice(toolBarPositionSSB, choices=toolBarPositions)
        self._toolBarPosition.SetSizerProps(expand=True, proportion=1)

        projectTabPositions = [s.value for s in ProjectTabPosition]
        del projectTabPositions[-1]     # Assumes last item is the "NOT_SET" marker

        projectPositionSSB: SizedStaticBox = SizedStaticBox(positionPanel, label='Project Tab Position', style=BORDER_THEME)
        projectPositionSSB.SetSizerProps(expand=True, proportion=1)

        self._projectTabPosition = Choice(projectPositionSSB, choices=projectTabPositions)
        self._projectTabPosition.SetSizerProps(expand=True, proportion=1)

    def _setControlValues(self):
        """

        """
        self._directorySelector.directoryPath = self._preferences.diagramsDirectory

        chosen:     str = self._preferences.fileHistoryDisplay.value
        historyIdx: int = self._projectHistoryPathPref.FindString(chosen)

        self._projectHistoryPathPref.SetSelection(historyIdx)

        iconSizeValue: ToolBarIconSize = self._preferences.toolBarIconSize
        iconSizeIdx:    int = self._toolBarIconSizePref.FindString(string=iconSizeValue.value)
        self._toolBarIconSizePref.SetSelection(iconSizeIdx)

        toolbarPosition: ToolBarPosition = self._preferences.toolBarPosition
        tbIdx:           int             = self._toolBarPosition.FindString(toolbarPosition.value)
        self._toolBarPosition.SetSelection(tbIdx)

        projectTabPosition: ProjectTabPosition = self._preferences.projectTabPosition
        ptIdx:              int                = self._projectTabPosition.FindString(projectTabPosition.value)
        self._projectTabPosition.SetSelection(ptIdx)

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
        self.logger.info(f'File History Path Preference changed.  {newValue=}')
        newPreference: ProjectHistoryDisplayType = ProjectHistoryDisplayType(newValue)
        self._preferences.fileHistoryDisplay = newPreference

    def _onToolBarIconSizePrefChanged(self, event: CommandEvent):

        newValue: str = event.GetString()
        self.logger.info(f'Tool Bar Icon Size Preference changed.  {newValue=}')
        newPreference: ToolBarIconSize = ToolBarIconSize(newValue)
        self._preferences.toolBarIconSize = newPreference

    def _pathChangedCallback(self, newPath: Path):
        self._preferences.diagramsDirectory = str(newPath)

    def _onToolBarPositionValueChanged(self, event: CommandEvent):
        valueStr: str = event.GetString()

        self._preferences.toolBarPosition = valueStr
        self._restartNeededMessage()

    def _onProjectTabPositionValueChanged(self, event: CommandEvent):
        valueStr: str = event.GetString()

        self._preferences.projectTabPosition = valueStr

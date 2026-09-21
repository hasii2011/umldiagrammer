
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CANCEL
from wx import DEFAULT_DIALOG_STYLE
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import NB_FIXEDWIDTH
from wx import NB_TOP
from wx import OK
from wx import YES_NO
from wx import NO_DEFAULT
from wx import ICON_QUESTION
from wx import ID_ANY
from wx import ID_OK
from wx import ID_YES
from wx import RESIZE_BORDER

from wx import CommandEvent
from wx import MessageDialog
from wx import Notebook
from wx import Size

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.preferences.DefaultValuesPanel import DefaultValuesPanel
from umlshapes.dialogs.preferences.DiagramPreferencesPanel import DiagramPreferencesPanel

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.dialogs.GeneralPreferencesPanel import GeneralPreferencesPanel
from umldiagrammer.dialogs.StartupPreferencesPanel import StartupPreferencesPanel

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

#
#
# from umlextensions.ui.preferences.ExtensionsPreferencesPage import ExtensionsPreferencesPage
#

class DlgPreferences(SizedDialog):
    """
    This class is the UML Diagrammer's preference dialog.

    Display the current preferences, the possible values, and save modified values.

    This works like preferences on OS X work.  They are changed
    immediately

    To use it from a wxFrame:
    ```python

        with DlgPreferences(parent=self._sizedFrame, appPubSubEngine=self._appPubSubEngine) as dlg:
            dlg.ShowModal()
    ```
    """
    def __init__(self, parent, appPubSubEngine: IAppPubSubEngine):
        """
        Args:
            parent:
        """
        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        style:   int  = DEFAULT_DIALOG_STYLE | RESIZE_BORDER
        dlgSize: Size = Size(width=460, height=600)
        super().__init__(parent, ID_ANY, "Diagrammer Preferences", size=dlgSize, style=style)

        self.logger:  Logger          = getLogger(__name__)

        self._preferences: DiagrammerPreferences = DiagrammerPreferences()

        self._generalPreferencesPanel: GeneralPreferencesPanel = cast(GeneralPreferencesPanel, None)
        self._startupPreferencesPanel: StartupPreferencesPanel = cast(StartupPreferencesPanel, None)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True)

        self._createTheControls(sizedPanel=sizedPanel)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK))

        self.Bind(EVT_BUTTON, self._onOk, id=ID_OK)
        self.Bind(EVT_CLOSE, self._onClose)
        # self.Fit()
        # self.SetMinSize(self.GetSize())

    @property
    def restartRequired(self) -> bool:
        return self._generalPreferencesPanel.restartRequired

    def _createTheControls(self, sizedPanel: SizedPanel):
        """
        Initialize the controls and add them each as a notebook page.
        """
        style: int = NB_TOP | NB_FIXEDWIDTH
        book: Notebook = Notebook(sizedPanel, style=style)
        book.SetSizerProps(expand=True, proportion=1)

        self._generalPreferencesPanel = GeneralPreferencesPanel(book, appPubSubEngine=self._appPubSubEngine)
        self._startupPreferencesPanel = StartupPreferencesPanel(parent=book, appPubSubEngine=self._appPubSubEngine)
        valuePreferences:         DefaultValuesPanel      = DefaultValuesPanel(parent=book)
        diagramPreferences:       DiagramPreferencesPanel = DiagramPreferencesPanel(parent=book)
        # positioningPreferences: PositioningPreferencesPage   = PositioningPreferencesPage(book, eventEngine=self._eventEngine)
        # pluginPreferences:      PluginPreferencesPage        = PluginPreferencesPage(book)
        # #
        book.AddPage(self._generalPreferencesPanel, text=self._generalPreferencesPanel.name, select=True)
        book.AddPage(self._startupPreferencesPanel, text=self._startupPreferencesPanel.name, select=False)
        book.AddPage(valuePreferences,         text=valuePreferences.name,         select=False)
        book.AddPage(diagramPreferences,       text=diagramPreferences.name,       select=False)
        # book.AddPage(positioningPreferences, text=positioningPreferences.name, select=False)
        # book.AddPage(pluginPreferences,      text=pluginPreferences.name,      select=False)

    def _onClose(self, event):

        self._potentiallyDisplayInfoMessage()
        self.EndModal(CANCEL)
        event.Skip(skip=True)

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):

        self._potentiallyDisplayInfoMessage()

        self.EndModal(OK)
        event.Skip(skip=True)

    def _potentiallyDisplayInfoMessage(self):
        """
        Prompt the user to restart now or later if any visual preferences changed.
        """
        if self.restartRequired is True:
            promptMessage: str = 'Visual preferences have changed.  Restart UML Diagrammer now to apply these changes?'
            askDialog: MessageDialog = MessageDialog(
                parent=self,
                message=promptMessage,
                caption='Restart Confirmation',
                style=YES_NO | NO_DEFAULT | ICON_QUESTION
            )
            dialogResponse: int = askDialog.ShowModal()
            askDialog.Destroy()
            if dialogResponse == ID_YES:
                self._appPubSubEngine.sendMessage(
                    messageType=MessageType.RESTART_APPLICATION_REQUEST,
                    uniqueId=APPLICATION_FRAME_ID
                )

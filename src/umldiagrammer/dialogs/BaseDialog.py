
from typing import Callable
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import OK
from wx import ID_OK
from wx import CANCEL
from wx import ID_CANCEL
from wx import EVT_BUTTON
from wx import STAY_ON_TOP
from wx import DEFAULT_DIALOG_STYLE

from wx import Button
from wx import CommandEvent

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

@dataclass
class CustomDialogButton:
    label:    str = ''
    callback: Callable = cast(Callable, None)


CustomDialogButtons = NewType('CustomDialogButtons', List[CustomDialogButton])


class BaseDialog(SizedDialog):
    def __init__(self, parent, title=''):

        super().__init__(parent, title=title, style=DEFAULT_DIALOG_STYLE | STAY_ON_TOP)

        self.logger: Logger = getLogger(__name__)

    def _layoutCustomDialogButtonContainer(self, parent: SizedPanel, customButtons: CustomDialogButtons):
        """
        Create Ok and Cancel
        Since we want to use a custom button set, we will not use the
        CreateStdDialogBtnSizer here, we'll create our own panel with
        a horizontal layout and add the buttons to that

        Args:
            parent:
            customButtons:  Data to create any necessary custom buttons
        """
        buttonPanel: SizedPanel = SizedPanel(parent)
        buttonPanel.SetSizerType('horizontal')
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        for customButton in customButtons:
            customDialogButton: CustomDialogButton = cast(CustomDialogButton, customButton)
            button:             Button             = Button(buttonPanel, label=customDialogButton.label)
            self.Bind(EVT_BUTTON, customDialogButton.callback, button)

        self._btnCancel = Button(buttonPanel, ID_CANCEL, '&Cancel')
        self._btnOk     = Button(buttonPanel, ID_OK, '&Ok')

        self.Bind(EVT_BUTTON, self._onOk,    self._btnOk)
        self.Bind(EVT_BUTTON, self._onClose, self._btnCancel)

        self._btnOk.SetDefault()

    def _onOk(self, _event: CommandEvent):
        """
        """
        self.EndModal(OK)

    def _onClose(self, _event: CommandEvent):
        """
        """
        self.EndModal(CANCEL)

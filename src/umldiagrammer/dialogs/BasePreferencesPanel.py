
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod

from wx import OK
from wx import BORDER_DEFAULT
from wx import ICON_WARNING


from wx import Window
from wx import MessageDialog

from wx.lib.sized_controls import SizedPanel

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences


class MyMetaBasePreferencesPage(ABCMeta, type(SizedPanel)):        # type: ignore
    """
    I have no idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass


class BasePreferencesPanel(SizedPanel, ABC, metaclass=MyMetaBasePreferencesPage):

    def __init__(self, parent: Window, style: int = BORDER_DEFAULT):

        super().__init__(parent, style=style)

        self._preferences: DiagrammerPreferences = DiagrammerPreferences()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _setControlValues(self):
        pass

    def _fixPanelSize(self, panel: SizedPanel):
        """
        Use this method or a dialog will not get resized correctly
        A little trick to make sure that the sizer cannot be resized to
        less screen space than the controls needs;

        Args:
            panel:
        """
        panel.Fit()
        panel.SetMinSize(panel.GetSize())

    def _restartNeededMessage(self):

        msgDlg: MessageDialog = MessageDialog(
            parent=None,
            message='You need to restart the UML Diagrammer to see this change',
            caption='Warning',
            style=OK | ICON_WARNING
        )
        msgDlg.ShowModal()

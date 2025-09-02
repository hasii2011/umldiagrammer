
from typing import List
from typing import NewType
from typing import Tuple
from typing import cast

from dataclasses import dataclass

from wx import CAPTION
from wx import CLOSE_BOX
from wx import EVT_BUTTON
from wx import EVT_CLOSE

from wx import FONTFAMILY_ROMAN
from wx import FONTWEIGHT_SEMIBOLD
from wx import ID_ANY
from wx import DefaultPosition
from wx import ID_OK
from wx import LI_HORIZONTAL
from wx import OK
from wx import RESIZE_BORDER
from wx import STAY_ON_TOP
from wx import Size
from wx import StaticLine
from wx import WHITE

from wx import StaticText
from wx import Font

from wx import CommandEvent
from wx import StaticBitmap
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umldiagrammer import __version__ as diagrammerVersion
from umldiagrammer.Versions import Versions

from umldiagrammer.resources.icons.AboutDialogLogo import embeddedImage as AboutDialogLogo

@dataclass
class VersionDescriptor:
    name:    str = ''
    version: str = ''


VersionDescriptors = NewType('VersionDescriptors', List[VersionDescriptor])


class DlgAbout(SizedDialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        title: str = f"About UML Diagrammer {diagrammerVersion}"
        style: int = RESIZE_BORDER | CAPTION | CLOSE_BOX | STAY_ON_TOP
        super().__init__(parent, wxID, title, DefaultPosition, style=style)

        self._versionFont: Font = self.GetFont()
        self._versionFont.SetFamily(FONTFAMILY_ROMAN)
        self._versionFont.SetPointSize(pointSize=12)
        self._versionFont.SetWeight(FONTWEIGHT_SEMIBOLD)

        self._versions: Versions = Versions()
        # Main panel
        mainPanel:  SizedPanel = self.GetContentsPane()
        mainPanel.SetSizerType("horizontal")
        mainPanel.SetSizerProps(expand=True, proportion=1)

        self._layoutDialog(parentPanel=mainPanel)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK))

        self.SetBackgroundColour(WHITE)

        self.Bind(EVT_BUTTON, self._onOk, id=ID_OK)
        self.Bind(EVT_CLOSE,  self._onOk)

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        Handle user click on the OK button
        """
        self.EndModal(OK)

    def _layoutDialog(self, parentPanel: SizedPanel):

        StaticBitmap(parentPanel, ID_ANY, AboutDialogLogo.GetBitmap(), size=Size(128, 128))

        self._layoutVersionsContainer(parentPanel=parentPanel)

    def _layoutVersionsContainer(self, parentPanel: SizedPanel):
        """
        """
        versionPanel: SizedPanel = SizedPanel(parent=parentPanel)
        versionPanel.SetSizerType('vertical')
        versionPanel.SetSizerProps(expand=True, proportion=1)

        versions: Versions = self._versions
        versionDescriptors: VersionDescriptors = VersionDescriptors(
            [
                VersionDescriptor(name=f'{versions.applicationName}', version=f'{versions.applicationVersion}'),
                VersionDescriptor(name=f'Platform:',   version=f'{versions.platform}'),
                VersionDescriptor(name=f'Python:',     version=f'{versions.pythonVersion}'),
            ]
        )
        appPackageDescriptors: VersionDescriptors = VersionDescriptors(
            [
                VersionDescriptor(name=f'wxPython:',    version=f'{versions.wxPythonVersion}'),
                VersionDescriptor(name=f'Data Model:',  version=f'{versions.pyutModelVersion}'),
                VersionDescriptor(name=f'UmlIO:',       version=f'{versions.umlioVersion}'),
                VersionDescriptor(name=f'UmlShapes:',   version=f'{versions.umlShapesVersion}'),
                # VersionDescriptor(name=f'Plugins Platform:', version=f'{versions.pyutPluginsVersion}'),
            ]
        )
        self._layoutVersionGrid(parentPanel=versionPanel, versionDescriptors=versionDescriptors)
        separator: StaticLine = StaticLine(versionPanel, ID_ANY,  style=LI_HORIZONTAL)
        separator.SetSizerProps(expand=True)
        self._layoutVersionGrid(parentPanel=versionPanel, versionDescriptors=appPackageDescriptors)

    def _layoutVersionGrid(self, parentPanel: SizedPanel, versionDescriptors: VersionDescriptors):
        """
        Given the value descriptors lays them out in a grid parented by the parent panel
        Args:
            parentPanel:            The parent of the new grid
            versionDescriptors:     The value descriptions

        """

        gridPanel: SizedPanel = SizedPanel(parent=parentPanel)
        gridPanel.SetSizerType("grid", {"cols": 2})   # 2-column grid layout
        # gridPanel.SetSizerProps(expand=True, proportion=1)

        borderStyle: Tuple[List[str], int] = (['top', 'bottom', 'left', 'right'], 1)

        for d in versionDescriptors:
            versionDescriptor: VersionDescriptor = cast(VersionDescriptor, d)

            nameCtl:    StaticText = StaticText(gridPanel, ID_ANY, versionDescriptor.name,    style=CAPTION)
            versionCtl: StaticText = StaticText(gridPanel, ID_ANY, versionDescriptor.version, style=CAPTION)

            nameCtl.SetFont(self._versionFont)
            nameCtl.SetSizerProps(halign='left', expand=False,  border=borderStyle)

            versionCtl.SetFont(self._versionFont)
            versionCtl.SetSizerProps(halign='left', expand=False, border=borderStyle)

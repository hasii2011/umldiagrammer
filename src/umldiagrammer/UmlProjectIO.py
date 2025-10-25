
from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import FD_OVERWRITE_PROMPT
from wx import FD_SAVE
from wx import ICON_ERROR
from wx import ID_OK
from wx import OK

from wx import FileDialog
from wx import MessageDialog

from umlio.IOTypes import DEFAULT_PROJECT_PATH
from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import UmlProject

from umlio.Reader import Reader
from umlio.Writer import Writer

from umldiagrammer.DiagrammerTypes import NOTEBOOK_ID

from umldiagrammer.preferences.DiagrammerPreferences import DiagrammerPreferences

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType


class UmlProjectIO:
    """
    I want to isolate the actual read/write calls through UML IO in this class
    """
    def __init__(self, appPubSubEngine: IAppPubSubEngine):
        """

        Args:
            appPubSubEngine:
        """

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

        self.logger:       Logger                = getLogger(__name__)
        self._preferences: DiagrammerPreferences = DiagrammerPreferences()

    def readProject(self, fileToOpen: str) -> UmlProject:
        """

        Args:
            fileToOpen:

        Returns:  The UML Project
        """
        reader:     Reader    = Reader()
        umlProject: UmlProject = reader.readProjectFile(fileName=Path(fileToOpen))

        return umlProject

    def saveProject(self, umlProject: UmlProject):

        fileName: Path = umlProject.fileName
        if fileName == DEFAULT_PROJECT_PATH:
            self.doFileSaveAs(umlProject=umlProject)
        else:
            self.logger.info(f'{fileName=}')
            if fileName.suffix != PROJECT_SUFFIX:
                if self._preferences.saveOnlyWritesCompressed is True:
                    newFilename: Path = Path(fileName.with_suffix(PROJECT_SUFFIX))
                    umlProject.fileName = newFilename
                else:
                    assert False, 'Write as XML not yet supported'

            writer: Writer = Writer()
            writer.writeFile(umlProject=umlProject, fileName=umlProject.fileName)

    def doFileSaveAs(self, umlProject: UmlProject):
        """
        Actually do the file save as
        Args:
            umlProject:
        """
        with (FileDialog(None,
                         defaultDir=self._preferences.diagramsDirectory,
                         wildcard=f'UML Diagrammer File ({PROJECT_SUFFIX}|{PROJECT_SUFFIX}',
                         style=FD_SAVE | FD_OVERWRITE_PROMPT)
              as fDialog):
            if fDialog.ShowModal() == ID_OK:
                specifiedFileName: str = fDialog.GetPath()
                if self._isProjectAlreadyOpen(fileName=specifiedFileName) is True:
                    eMsg: str = f'Error ! This project `{Path(specifiedFileName).stem}` is currently open.  Please choose another name!'
                    with MessageDialog(None, eMsg, "Save change, filename error", OK | ICON_ERROR) as dlg:
                        dlg.ShowModal()
                else:
                    self.saveAsProject(umlProject, specifiedFileName)

    def saveAsProject(self, umlProject: UmlProject, specifiedFileName: str):
        """

        Args:
            umlProject:
            specifiedFileName:
        """
        oldName: Path = umlProject.fileName
        newName: Path = Path(specifiedFileName)
        umlProject.fileName = newName

        self._appPubSubEngine.sendMessage(messageType=MessageType.PROJECT_RENAMED,
                                          uniqueId=NOTEBOOK_ID,
                                          oldName=oldName.stem,
                                          newName=newName.stem
                                          )
        writer: Writer = Writer()
        writer.writeFile(umlProject=umlProject, fileName=umlProject.fileName)
        self._appPubSubEngine.sendMessage(messageType=MessageType.CURRENT_PROJECT_SAVED,
                                          uniqueId=NOTEBOOK_ID,
                                          projectPath=umlProject.fileName
                                          )
        self.logger.info(f'Project {oldName} saved as {newName}')

    def _isProjectAlreadyOpen(self, fileName: str) -> bool:
        """
        TODO:
        Args:
            fileName:

        Returns:

        """

        self.logger.info(f'{fileName=}')

        return False

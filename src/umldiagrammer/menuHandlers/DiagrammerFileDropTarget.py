
from typing import List
from typing import NewType

from logging import INFO
from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import ICON_ERROR
from wx import OK

from wx import FileDropTarget
from wx import MessageDialog

from wx import Yield as wxYield

from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import PROJECT_SUFFIX
from umlio.IOTypes import UmlProject

from umlio.Reader import Reader

from umldiagrammer.DiagrammerTypes import APPLICATION_FRAME_ID

from umldiagrammer.pubsubengine.IAppPubSubEngine import IAppPubSubEngine
from umldiagrammer.pubsubengine.MessageType import MessageType

FileNames = NewType('FileNames', List[str])


class DiagrammerFileDropTarget(FileDropTarget):

    def __init__(self, appPubSubEngine: IAppPubSubEngine):

        super().__init__()

        self.logger: Logger = getLogger(__name__)
        self.logger.setLevel(INFO)

        self._appPubSubEngine: IAppPubSubEngine = appPubSubEngine

    def OnDropFiles(self, x: int, y: int, filenames: FileNames) -> bool:
        """

        Args:
            x:  abscissa of dropped files
            y:  ordinate of dropped files
            filenames:   List of strings which are the full path names of the dropped files
        """

        badFileNameList: FileNames = FileNames([])
        fileNameList:    FileNames = FileNames([])

        for fileName in filenames:
            self.logger.info(f'You dropped: {fileName}')
            if fileName.endswith(XML_SUFFIX) or fileName.endswith(PROJECT_SUFFIX):
                fileNameList.append(fileName)
            else:
                badFileNameList.append(fileName)

        self._loadFiles(fileNameList)

        if len(badFileNameList) > 0:
            message: str    = f'Only {PROJECT_SUFFIX} and {XML_SUFFIX} files are supported'
            caption: str    = 'Unsupported File Type'
            booBoo: MessageDialog = MessageDialog(parent=None, message=message, caption=caption, style=OK | ICON_ERROR)
            booBoo.ShowModal()

        return True

    def _loadFiles(self, filenames: FileNames):

        for filename in filenames:
            wxYield()
            self._loadDroppedFile(filename=filename)

        return True

    def _loadDroppedFile(self, filename: str):
        """

        Args:
            filename:  Should end with either PROJECT_SUFFIX or XML_SUFFIX
        """

        fileNamePath: Path   = Path(filename)
        suffix:       str    = fileNamePath.suffix
        reader:       Reader = Reader()
        if suffix == XML_SUFFIX:
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(fileNamePath))
            self._appPubSubEngine.sendMessage(messageType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, umlProject=umlProject)

        elif suffix == PROJECT_SUFFIX:
            umlProject = reader.readProjectFile(fileName=fileNamePath)
            self._appPubSubEngine.sendMessage(messageType=MessageType.OPEN_PROJECT, uniqueId=APPLICATION_FRAME_ID, umlProject=umlProject)

        else:
            assert False, 'We should not get files with bad suffixes'

    def _displayError(self, message: str):

        booBoo: MessageDialog = MessageDialog(parent=None, message=message, caption='Bad Drop File', style=OK | ICON_ERROR)
        booBoo.ShowModal()

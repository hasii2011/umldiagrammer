
from codeallybasic.SingletonV3 import SingletonV3

from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions
from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import KeyName

from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize

DEFAULT_TB_ICON_SIZE:     str = ToolBarIconSize.SIZE_32.value

SECTION_GENERAL: ValueDescriptions = ValueDescriptions(
    {
        KeyName('toolBarIconSize'): ValueDescription(defaultValue=DEFAULT_TB_ICON_SIZE,  deserializer=ToolBarIconSize.deSerialize, enumUseValue=True),
    }
)


DIAGRAMMER_SECTIONS: Sections = Sections(
    {
        SectionName('General'): SECTION_GENERAL,
    }
)

class DiagrammerPreferences(DynamicConfiguration, metaclass=SingletonV3):

    def __init__(self):

        super().__init__(baseFileName='umlDiagrammer.ini', moduleName='umlDiagrammer', sections=DIAGRAMMER_SECTIONS)

        self._overrideProgramExitSize:     bool = False
        self._overrideProgramExitPosition: bool = False

        self._configParser.optionxform = str  # type: ignore

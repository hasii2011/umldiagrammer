
from codeallybasic.Position import Position
from codeallybasic.Dimensions import Dimensions
from codeallybasic.SingletonV3 import SingletonV3
from codeallybasic.SecureConversions import SecureConversions

from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions
from codeallybasic.DynamicConfiguration import DynamicConfiguration

from umldiagrammer.preferences.FileHistoryPreference import FileHistoryPreference

from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize

DEFAULT_TB_ICON_SIZE:     str = ToolBarIconSize.SIZE_32.value
DEFAULT_STARTUP_SIZE:     str = Dimensions(1024, 768).__str__()
DEFAULT_STARTUP_POSITION: str = Position(5, 5).__str__()

DEFAULT_FILE_HISTORY_DISPLAY: str = FileHistoryPreference.SHOW_NEVER.value

SECTION_GENERAL: ValueDescriptions = ValueDescriptions(
    {
        KeyName('loadLastOpenedProject'):   ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('autoResizeShapesOnEdit'):  ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('diagramsDirectory'):       ValueDescription(defaultValue=''),

        KeyName('toolBarIconSize'):         ValueDescription(defaultValue=DEFAULT_TB_ICON_SIZE,         deserializer=ToolBarIconSize.deSerialize, enumUseValue=True),
        KeyName('fileHistoryDisplay'):      ValueDescription(defaultValue=DEFAULT_FILE_HISTORY_DISPLAY, deserializer=FileHistoryPreference,       enumUseValue=True),
    }
)

SECTION_STARTUP: ValueDescriptions = ValueDescriptions (
    {
        KeyName('fullScreen'):         ValueDescription(defaultValue='False',                  deserializer=SecureConversions.secureBoolean),
        KeyName('startupSize'):        ValueDescription(defaultValue=DEFAULT_STARTUP_SIZE,     deserializer=Dimensions.deSerialize),
        KeyName('centerAppOnStartup'): ValueDescription(defaultValue='False',                  deserializer=SecureConversions.secureBoolean),
        KeyName('startupPosition'):    ValueDescription(defaultValue=DEFAULT_STARTUP_POSITION, deserializer=Position.deSerialize),
    }
)

DIAGRAMMER_SECTIONS: Sections = Sections(
    {
        SectionName('General'): SECTION_GENERAL,
        SectionName('Startup'): SECTION_STARTUP,
    }
)

class DiagrammerPreferences(DynamicConfiguration, metaclass=SingletonV3):

    def __init__(self):

        super().__init__(baseFileName='umlDiagrammer.ini', moduleName='umlDiagrammer', sections=DIAGRAMMER_SECTIONS)

        self._overrideProgramExitSize:     bool = False
        self._overrideProgramExitPosition: bool = False

        self._configParser.optionxform = str  # type: ignore

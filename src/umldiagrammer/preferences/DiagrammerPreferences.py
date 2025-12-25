
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

from umldiagrammer.preferences.ProjectHistoryDisplayType import ProjectHistoryDisplayType

from umldiagrammer.toolbar.ToolBarIconSize import ToolBarIconSize
from umldiagrammer.toolbar.ToolBarPosition import ToolBarPosition

DEFAULT_TB_ICON_SIZE:     str = ToolBarIconSize.SMALL.value
DEFAULT_STARTUP_SIZE:     str = Dimensions(1024, 768).__str__()
DEFAULT_STARTUP_POSITION: str = Position(5, 5).__str__()

TEST_POSITION: str = Position(20, 40).__str__()
TEST_SIZE:     str = str(Dimensions(1247, 842))

DEFAULT_FILE_HISTORY_DISPLAY: str = ProjectHistoryDisplayType.SHOW_NEVER.value
DEFAULT_TOOLBAR_POSITION:     str = ToolBarPosition.LEFT.value

SECTION_GENERAL: ValueDescriptions = ValueDescriptions(
    {
        KeyName('loadLastOpenedProject'):   ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('autoResizeShapesOnEdit'):  ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('diagramsDirectory'):       ValueDescription(defaultValue=''),

        KeyName('toolBarIconSize'):         ValueDescription(defaultValue=DEFAULT_TB_ICON_SIZE,         deserializer=ToolBarIconSize.deSerialize, enumUseValue=True),
        KeyName('fileHistoryDisplay'):      ValueDescription(defaultValue=DEFAULT_FILE_HISTORY_DISPLAY, deserializer=ProjectHistoryDisplayType, enumUseValue=True),

        KeyName('saveOnlyWritesCompressed'): ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
    }
)

SECTION_STARTUP: ValueDescriptions = ValueDescriptions (
    {
        KeyName('fullScreen'):         ValueDescription(defaultValue='False',                  deserializer=SecureConversions.secureBoolean),
        KeyName('startupSize'):        ValueDescription(defaultValue=DEFAULT_STARTUP_SIZE,     deserializer=Dimensions.deSerialize),
        KeyName('centerAppOnStartup'): ValueDescription(defaultValue='False',                  deserializer=SecureConversions.secureBoolean),
        KeyName('startupPosition'):    ValueDescription(defaultValue=DEFAULT_STARTUP_POSITION, deserializer=Position.deSerialize),
        KeyName('toolBarPosition'):    ValueDescription(defaultValue=DEFAULT_TOOLBAR_POSITION, deserializer=ToolBarPosition),
    }
)
SECTION_DEBUG: ValueDescriptions = ValueDescriptions(
    {
        KeyName('inTestMode'):   ValueDescription(defaultValue='False',       deserializer=SecureConversions.secureBoolean),
        KeyName('testPosition'): ValueDescription(defaultValue=TEST_POSITION, deserializer=Position.deSerialize),
        KeyName('testSize'):     ValueDescription(defaultValue=TEST_SIZE,     deserializer=Dimensions.deSerialize),
    }
)
DIAGRAMMER_SECTIONS: Sections = Sections(
    {
        SectionName('General'): SECTION_GENERAL,
        SectionName('Startup'): SECTION_STARTUP,
        SectionName('Debug'):   SECTION_DEBUG,
    }
)

class DiagrammerPreferences(DynamicConfiguration, metaclass=SingletonV3):

    def __init__(self):

        super().__init__(baseFileName='umlDiagrammer.ini', moduleName='umlDiagrammer', sections=DIAGRAMMER_SECTIONS)

        self._overrideProgramExitSize:     bool = False
        self._overrideProgramExitPosition: bool = False

        self._configParser.optionxform = str  # type: ignore

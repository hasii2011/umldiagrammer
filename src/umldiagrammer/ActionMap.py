
from typing import Dict

from umldiagrammer.UIAction import UIAction
from umldiagrammer.UIIdentifiers import UIIdentifiers

#
# wxPython either via a menu selection or a toolbar click issues a wxPython
# event.  We have to convert that to something the UML Diagrammer wants
# to do.  That is called a UI Action.
# We set the UI into a mode where we wait for the next UmlFrame click
# event from the umlshapes module.  When we get that event we check which
# UI Action mode we are in and do that
#
#
ActionMap: Dict[int, UIAction] = {
    UIIdentifiers.ID_ARROW:                    UIAction.SELECTOR,
    UIIdentifiers.ID_CLASS:                    UIAction.NEW_CLASS,
    UIIdentifiers.ID_NOTE:                     UIAction.NEW_NOTE,
    UIIdentifiers.ID_RELATIONSHIP_INHERITANCE: UIAction.NEW_INHERIT_LINK,
    UIIdentifiers.ID_RELATIONSHIP_REALIZATION: UIAction.NEW_IMPLEMENT_LINK,

    UIIdentifiers.ID_RELATIONSHIP_COMPOSITION: UIAction.NEW_COMPOSITION_LINK,
    UIIdentifiers.ID_RELATIONSHIP_AGGREGATION: UIAction.NEW_AGGREGATION_LINK,
    UIIdentifiers.ID_RELATIONSHIP_ASSOCIATION: UIAction.NEW_ASSOCIATION_LINK,
    UIIdentifiers.ID_RELATIONSHIP_NOTE:        UIAction.NEW_NOTE_LINK,
    UIIdentifiers.ID_ACTOR:                    UIAction.NEW_ACTOR,
    UIIdentifiers.ID_TEXT:                     UIAction.NEW_TEXT,
    UIIdentifiers.ID_USECASE:                  UIAction.NEW_USECASE,
    UIIdentifiers.ID_SD_INSTANCE:              UIAction.NEW_SD_INSTANCE,
    UIIdentifiers.ID_SD_MESSAGE:               UIAction.NEW_SD_MESSAGE,
}


from dataclasses import dataclass

from umlio.IOTypes import UmlProject


@dataclass
class ProjectDossier:
    umlProject: UmlProject
    modified:   bool = False

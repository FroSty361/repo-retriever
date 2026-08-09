from dataclasses import dataclass, field
from typing import List

MAX_SAVED_PREVIOUS_REPOSITORIES = 8

class PreviousRepositoriesList(list):
    def append(self, repository: dict):
        while len(super()) >= MAX_SAVED_PREVIOUS_REPOSITORIES:
            super().pop(0)

        super().append(repository)

@dataclass
class UserSettings:
    is_light_mode: bool = False
    previous_repositories: List[dict] = field(default_factory=PreviousRepositoriesList, init=False, repr=False)
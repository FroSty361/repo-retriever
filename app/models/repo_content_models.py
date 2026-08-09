from dataclasses import dataclass, field

@dataclass
class RepoContentItem:
    name: str
    url: str

    parent_folder: str # Check By url

@dataclass
class RepoDirectory(RepoContentItem):
    directories: list[RepoDirectory] = field(default_factory=list, init=False, repr=False)
    files: list[RepoFile] = field(default_factory=list, init=False, repr=False)

@dataclass
class RepoFile(RepoContentItem):
    download_url: str
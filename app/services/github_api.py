import requests
import base64
from typing import List
from models.repo_content_models import RepoContentItem, RepoFile, RepoDirectory

def get_github_repo_data(repoOwner: str, repoName: str):
    repoURL = f"https://api.github.com/repos/{repoOwner}/{repoName}"

    headers = {"Accept": "application/vnd.github+json"}

    response = requests.get(f"{repoURL}/contents", headers=headers)

    print(response.status_code)

    if response.status_code == 200:
        data = response.json()

        root_directory = RepoDirectory(name=repoName, url=repoURL, parent_folder="")

        for page in data:
            if page["type"] == "file":
                name: str = page["name"]
                url: str = page["url"]
                parent_folder: str = root_directory.url
                download_url = page["download_url"]

                repo_file: RepoFile = RepoFile(name=name, url=url, parent_folder=parent_folder, download_url=download_url)

                root_directory.files.append(repo_file)
            elif page["type"] == "dir":
                sub_directory: RepoDirectory = get_github_repo_directory_content(page["name"], page["url"], root_directory.url)

                if sub_directory is not None:
                    root_directory.directories.append(sub_directory)

        return root_directory, True
    else:
        return {}, False

def get_github_repo_directory_content(name: str, url: str, parent_directory_url: str) -> RepoContentItem | None:
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    directory = RepoDirectory(name=name, url=url, parent_folder=parent_directory_url)

    for page in data:
        if page["type"] == "file":
            name: str = page["name"]
            url: str = page["url"]
            parent_folder: str = directory.url
            download_url = page["download_url"]

            repo_file: RepoFile = RepoFile(name=name, url=url, parent_folder=parent_folder, download_url=download_url)

            directory.files.append(repo_file)
        elif page["type"] == "dir":
            sub_directory: RepoDirectory = get_github_repo_directory_content(page["name"], url, directory.url)

            if directory is None:
                directory.directories.append(sub_directory)

    return directory
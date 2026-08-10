import os
import requests
import base64
from typing import List
from models.repo_content_models import RepoContentItem, RepoFile, RepoDirectory
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def get_github_repo_data(repoOwner: str, repoName: str) -> RepoContentItem | None:
    repoURL = f"https://api.github.com/repos/{repoOwner}/{repoName}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

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

        return root_directory
    else:
        return None

def get_github_repo_directory_content(name: str, url: str, parent_directory_url: str) -> RepoContentItem | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    directory = RepoDirectory(name=name, url=url, parent_folder=parent_directory_url)

    print(data)

    for page in data:
        if page["type"] == "file":
            file_name: str = page["name"]
            file_url: str = page["url"]
            parent_folder: str = directory.url
            download_url = page["download_url"]

            repo_file: RepoFile = RepoFile(name=file_name, url=file_url, parent_folder=parent_folder, download_url=download_url)

            directory.files.append(repo_file)
        elif page["type"] == "dir":
            dir_name: str = page["name"]
            dir_url: str = page["url"]

            sub_directory: RepoDirectory = get_github_repo_directory_content(dir_name, dir_url, directory.url)

            if sub_directory is not None:
                directory.directories.append(sub_directory)

    return directory
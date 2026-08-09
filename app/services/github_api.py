import requests
import base64
from typing import List

def get_github_repo_data(repoOwner: str, repoName: str):
    repoURL = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents"

    headers = {"Accept": "application/vnd.github+json"}

    response = requests.get(repoURL, headers=headers)

    if response.status_code == 200:
        data = response.json()

        repo_contents = []

        for page in data:
            if page["type"] == "file":
                repo_contents.append(page["name"])
            elif page["type"] == "dir":
                repo_contents = get_github_repo_directory_content(page["url"], repo_contents)

        print(repo_contents)

        return repo_contents, True
    else:
        return {}, False

def get_github_repo_directory_content(url: str, repo_contents):
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return repo_contents

    data = response.json()

    for page in data:
        if page["type"] == "file":
            repo_contents.append(page["name"])
        elif page["type"] == "dir":
            repo_contents.append(page["name"])

            repo_contents = get_github_repo_directory_content(page["url"], repo_contents)

    return repo_contents
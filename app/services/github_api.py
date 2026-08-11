import base64
import os
import requests
from dotenv import load_dotenv
from flask import url_for

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def get_github_repo_directory_tree(repoOwner: str, repoName: str) -> str | None:
    repoURL = f"https://api.github.com/repos/{repoOwner}/{repoName}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(f"{repoURL}/contents", headers=headers)

    if response.status_code == 200:
        data = response.json()

        html = f"<li><span class='caret'><a href='https://github.com/{repoOwner}/{repoName}'>{repoName}</a></span>\n"
        html += "<ul class='nested'>\n"

        for page in data:
            if page["type"] == "file":
                file_name: str = page["name"]
                file_url: str = page["url"]
                file_url_encoded_bytes = base64.urlsafe_b64encode(file_url.encode('utf-8'))
                file_url_encoded = file_url_encoded_bytes.decode('utf-8')

                view_file_link = url_for('result.view_file', file_url_encoded=file_url_encoded)

                html += f"<li><a href='{view_file_link}'>{file_name}</a></li>\n"
            elif page["type"] == "dir":
                sub_directory = get_github_repo_directory_html(page["name"], page["url"])

                if sub_directory is not None:
                    html += sub_directory

        html += "</ul>\n"
        html += "</li>\n"

        return html
    else:
        return None

def get_github_repo_directory_html(name: str, url: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    html = f"<li><span class='caret'><a href='{url}'>{name}</a></span>\n"
    html += "<ul class='nested'>\n"

    for page in data:
        if page["type"] == "file":
            file_name: str = page["name"]
            file_url: str = page["url"]
            file_url_encoded_bytes = base64.urlsafe_b64encode(file_url.encode('utf-8'))
            file_url_encoded = file_url_encoded_bytes.decode('utf-8')

            view_file_link = url_for('result.view_file', file_url_encoded=file_url_encoded)

            html += f"<li><a href='{view_file_link}'>{file_name}</a></li>\n"
        elif page["type"] == "dir":
            dir_name: str = page["name"]
            dir_url: str = page["url"]

            sub_directory = get_github_repo_directory_html(dir_name, dir_url)

            if sub_directory is not None:
                html += sub_directory

    html += "</ul>\n"
    html += "</li>\n"

    return html

def get_file_data(file_url: str) -> dict | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(file_url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    file_data = {}

    file_data["name"] = data["name"]
    file_data["path"] = data["path"]

    unviewable_mime_types = [ "image/png", "image/jpeg", "image/gif", "image/avif",
                              "audio/mpeg", "video/mp4", "video/x-msvideo",
                              "video/x-msvideo", "video/x-msvideo", "video/x-msvideo",
                              "application/octet-stream", "application/x-dosexec",
                              "application/zip", "application/x-tar", "application/x-gzip"
                              "application/pdf"]

    try:
        response = requests.head(data["download_url"], allow_redirects=True)

        mime_type = response.headers.get("Content-Type")

        if mime_type:
            mime_type = mime_type.split(";")[0].strip()

        if mime_type in unviewable_mime_types:
            file_data["content"] = f"MIME Type {mime_type} Is Unviewable"

            print(file_data["content"])

            return file_data
    except requests.exceptions.RequestException as e:
        print(f"Could Not Fetch File Download URL For Getting MIME Type. Sending Current Data. Error = {e}")

        return file_data

    content_encoded = data["content"]
    content_decoded_bytes = base64.b64decode(content_encoded.encode('utf-8'))
    content = content_decoded_bytes.decode('utf-8')

    content = content.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
    content = content.replace("  ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    content = content.replace("   ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    content = content.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    content = content.replace('\n', '<br>')
    file_data["content"] = content

    return file_data
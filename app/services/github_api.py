import base64
import io
import os
import httpx
from dotenv import load_dotenv
from flask import url_for
import asyncio

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

async def get_github_repo_directory_tree(repoOwner: str, repoName: str, branch: str = "main") -> str | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    repoURL = f"https://api.github.com/repos/{repoOwner}/{repoName}/git/trees/{branch}?recursive=1"

    print(repoURL)

    async with httpx.AsyncClient(headers=headers) as httpx_client:
        response = await httpx_client.get(f"{repoURL}/contents")

        if response.status_code == 200:
            data = response.json()

            html = f"<li><span class='caret'><a href='https://github.com/{repoOwner}/{repoName}'>{repoName}</a></span>\n"
            html += "<ul class='nested'>\n"

            directory_depths = [0]

            for resource in data["tree"]:
                name = resource["path"].split("/")[-1]
                url: str = resource["url"]

                if resource["type"] == "blob":
                    file_url_encoded_bytes = base64.urlsafe_b64encode(url.encode('utf-8'))
                    file_url_encoded = file_url_encoded_bytes.decode('utf-8')

                    view_file_link = url_for('result.view_file', file_url_encoded=file_url_encoded)

                    html += f"<li><a href='{view_file_link}'>{name}</a>   <button type='button' onclick=\"downloadFile('{file_url_encoded}')\">Download</button></li>\n"
                elif resource["type"] == "tree":
                    print(resource)

                    directory_depth = len(resource["path"].split("/"))

                    while directory_depths and directory_depths[-1] >= directory_depth:
                        html += "</ul>\n"
                        html += "</li>\n"

                        directory_depths.pop()

                    html += f"<li><span class='caret'><a href='{url}'>{name}</a></span>\n"
                    html += "<ul class='nested'>\n"

                    directory_depths.append(directory_depth)

            html += "</ul>\n"
            html += "</li>\n"

            return html
        else:
            return None

async def get_github_repo_directory_html(name: str, url: str, httpx_client) -> str | None:
    response = await httpx_client.get(url)

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

            html += f"<li><a href='{view_file_link}'>{file_name}</a>   <button type='button' onclick=\"downloadFile('{file_url_encoded}')\">Download</button></li>\n"
        elif page["type"] == "dir":
            dir_name: str = page["name"]
            dir_url: str = page["url"]

            sub_directory = await get_github_repo_directory_html(dir_name, dir_url, httpx_client)

            if sub_directory is not None:
                html += sub_directory

    html += "</ul>\n"
    html += "</li>\n"

    return html

async def get_file_data(file_url: str) -> dict | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(file_url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    file_data = {}

    file_data["name"] = data["name"]
    file_data["path"] = data["path"]

    file_data["download_url"] = data["download_url"]

    unviewable_mime_types = [ "image/png", "image/jpeg", "image/gif", "image/avif",
                              "audio/mpeg", "video/mp4", "video/x-msvideo",
                              "video/x-msvideo", "video/x-msvideo", "video/x-msvideo",
                              "application/octet-stream", "application/x-dosexec",
                              "application/zip", "application/x-tar", "application/x-gzip"
                              "application/pdf"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(data["download_url"], headers=headers)

        mime_type = response.headers.get("Content-Type")

        if mime_type:
            mime_type = mime_type.split(";")[0].strip()

        if mime_type in unviewable_mime_types:
            file_data["content"] = f"MIME Type {mime_type} Is Unviewable"

            print(file_data["content"])

            return file_data
    except httpx.RequestError as e:
        print(f"Could Not Fetch File Download URL For Getting MIME Type. Sending Current Data. Error = {e}")

        return file_data

    content_encoded = data["content"]
    content_decoded_bytes = base64.b64decode(content_encoded.encode('utf-8'))
    content = content_decoded_bytes.decode('utf-8')

    html_content = content.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
    html_content = html_content.replace("  ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    html_content = html_content.replace("   ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    html_content = html_content.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    html_content = html_content.replace('\n', '<br>')
    file_data["html_content"] = html_content

    return file_data

async def get_raw_file_data(file_download_url: str):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(file_download_url, headers=headers)

    if response.status_code != 200:
        return None, None

    file_stream = io.BytesIO(response.content)

    return file_stream, response.headers.get('Content-Type')
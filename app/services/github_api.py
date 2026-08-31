import base64
import io
import zipfile
import os
import httpx
from dotenv import load_dotenv
from flask import url_for

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

async def get_github_repo_directory_tree(repoOwner: str, repoName: str, branch: str = "main") -> str | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    repoURL = f"https://api.github.com/repos/{repoOwner}/{repoName}/git/trees/{branch}?recursive=1"

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

                path = resource["path"]
                path_encoded_bytes = base64.urlsafe_b64encode(path.encode('utf-8'))
                path_encoded = path_encoded_bytes.decode('utf-8')

                if resource["type"] == "blob":
                    file_url_encoded_bytes = base64.urlsafe_b64encode(url.encode('utf-8'))
                    file_url_encoded = file_url_encoded_bytes.decode('utf-8')

                    view_file_link = url_for('result.view_file', path_encoded=path_encoded, file_url_encoded=file_url_encoded)

                    html += f"<li><a href='{view_file_link}'>{name}</a>   <button type='button' onclick=\"downloadFile('{path_encoded}', '{file_url_encoded}')\">Download</button></li>\n"
                elif resource["type"] == "tree":
                    print(resource)

                    directory_depth = len(resource["path"].split("/"))

                    while directory_depths and directory_depths[-1] >= directory_depth:
                        html += "</ul>\n"
                        html += "</li>\n"

                        directory_depths.pop()

                    directory_url_encoded_bytes = base64.urlsafe_b64encode(url.encode('utf-8'))
                    directory_url_encoded = directory_url_encoded_bytes.decode('utf-8')

                    html += f"<li><span class='caret'><a href='{url}'>{name}</a>   <button type='button' onclick=\"downloadDirectory('{path_encoded}', '{directory_url_encoded}')\">Download</button></span>\n"
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

async def get_file_data(path: str, blob_url: str) -> dict | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    repoOwner = blob_url.split("/")[4]
    repoName = blob_url.split("/")[5]
    file_url = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.get(file_url, headers=headers)

        if response.status_code != 200:
            return None

        data = response.json()

        file_data = {}

        file_data["name"] = data["name"]
        file_data["path"] = path

        download_url = data["download_url"]

        file_data["download_url"] = download_url

        print(download_url)

        unviewable_mime_types = [
            "image/png", "image/jpeg", "image/gif", "image/avif",
            "audio/mpeg", "video/mp4", "video/x-msvideo",
            "application/octet-stream", "application/x-dosexec",
            "application/zip", "application/x-tar",
            "application/x-gzip", "application/pdf"
        ]

        try:
            download_response = await client.get(download_url, headers=headers)

            mime_type = download_response.headers.get("Content-Type")

            if mime_type:
                mime_type = mime_type.split(";")[0].strip()

            if mime_type in unviewable_mime_types:
                file_data["content"] = f"MIME Type {mime_type} Is Unviewable"

                print(file_data["content"])

                return file_data

        except httpx.RequestError as e:
            print(f"Could Not Fetch File Download URL For Getting MIME Type. Sending Current Data. Error = {e}")

            return file_data

        content_encoded = data.get("content", "")

        if not content_encoded:
            file_data["html_content"] = ""

            return file_data

        content_decoded_bytes = base64.b64decode(content_encoded.encode("utf-8"))
        content = content_decoded_bytes.decode("utf-8")

        html_content = content.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        html_content = html_content.replace("  ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        html_content = html_content.replace("   ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        html_content = html_content.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        html_content = html_content.replace('\n', '<br>')

        file_data["html_content"] = html_content

        return file_data

async def get_directory_data(path: str, directory_url: str) -> dict | None:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    repoOwner = directory_url.split("/")[4]
    repoName = directory_url.split("/")[5]
    content_url = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.get(content_url, headers=headers)

    if response.status_code != 200:
        return None

    print(content_url)

    data = response.json()

    directory_data = {}

    directory_data["name"] = data[0]["name"]

    directory_data["path"] = path

    directory_data["content_url"] = data[0]["url"]

    return directory_data

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

async def get_directory_contents_data(directory_url: str):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(directory_url, headers=headers)

        if response.status_code != 200:
            return None

    data = response.json()

    file_stream = io.BytesIO()

    with zipfile.ZipFile(file_stream, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in data:
            if item['type'] == 'file':
                file_url = item['download_url']

                if not file_url:
                    continue

                file_data_response = await client.get(file_url, headers=headers)

                if file_data_response.status_code == 200:
                    zf.writestr(item["name"], file_data_response.content)

    file_stream.seek(0)

    return file_stream
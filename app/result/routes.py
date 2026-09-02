from flask import render_template, request, redirect, url_for, send_file
from services import github_api, arg_utils
from . import result
from markupsafe import Markup

@result.route("/repo-result/", methods=["GET", "POST"])
async  def repo_result():
    if request.method == "POST":
        repoOwner = str(request.form.get("repoOwner"))
        repoName = str(request.form.get("repoName"))
        repoBranch = str(request.form.get("repoBranch"))

        if repoBranch is None or repoBranch == "":
            repoBranch = "main"

        try:
            repo_html = await github_api.get_github_repo_directory_tree(repoOwner, repoName, repoBranch)
        except Exception as e:
            return f"An Error Occurred When Trying To Receive GitHub Direstory Tree HTML {e}", 500

        if repo_html is None or repo_html == "":
            print(f"Failed To Get Data For Github Repository By Owner {repoOwner} And Name {repoName}")

            return redirect(url_for('home.index'))

        return render_template("result/result.html", repo_name=repoName, repo=Markup(repo_html))

    return redirect(url_for('home.index'))

@result.route("/view-file/<path_encoded>/<file_url_encoded>")
async def view_file(path_encoded, file_url_encoded):
    path = arg_utils.decode_url_string(path_encoded)
    file_url = arg_utils.decode_url_string(file_url_encoded)

    try:
        file_data = await github_api.get_file_data(path, file_url)
    except Exception as e:
        return f"An Error Occurred When Trying To Get File Data For Viewing File {e}", 500

    if file_data is None or file_data == "":
        print(f"Failed To Get File Data {file_url} From Github Repository")

        return redirect(url_for('home.index'))

    return render_template("result/file-view.html", file_name=file_data["name"], file_path=file_data["path"], file_content=file_data["html_content"])

@result.route('/download-file/', methods=['POST'])
async def download_file():
    data = request.get_json()

    path_encoded = data["path"]
    path = arg_utils.decode_url_string(path_encoded)

    file_url_encoded = data["file_url"]
    file_url = arg_utils.decode_url_string(file_url_encoded)

    try:
        file_data = await github_api.get_file_data(path, file_url)

        print(f"File Data = {file_data}")
    except Exception as e:
        return f"An Error Occurred When Trying To Get File Data For Download {e}", 500

    if file_data is None or file_data == "":
        print(f"Failed To Get File Data {file_url} From Github Repository")

        return {"status": "400"}, 400

    download_url = file_data["download_url"]

    print(download_url)

    try:
        file_stream, content_type = await github_api.get_raw_file_data(download_url)

        if file_stream is None or content_type is None:
            print(f"Failed To Get Raw File Content From {download_url}")

            return {"status": "400"}, 400

        print(file_stream)

        response = send_file(
            file_stream,
            as_attachment=True,
            download_name=file_data["name"],
            mimetype=content_type
        )

        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response
    except Exception as e:
        return f"An Error Occurred When Trying To Get Raw File Data For Download {e}", 500

@result.route('/download-directory/', methods=['POST'])
async def download_directory():
    data = request.get_json()

    path_encoded = data["path"]
    path = arg_utils.decode_url_string(path_encoded)

    directory_url_encoded = data["directory_url"]
    directory_url = arg_utils.decode_url_string(directory_url_encoded)

    try:
        directory_data = await github_api.get_directory_data(path, directory_url)
    except Exception as e:
        return f"An Error Occurred When Trying To Get Directory Data For Download {e}", 500

    if directory_data is None or directory_data == "":
        print(f"Failed To Get Directory Data {directory_data} From Github Repository")

        return {"status": "400"}, 400

    url = directory_data["content_url"]

    print(f"URL = {url}")

    try:
        file_stream = await github_api.get_directory_contents_data(url, path)

        if file_stream is None:
            print(f"Failed To Get Raw Directory Content From {url}")

            return {"status": "400"}, 400

        response = send_file(
            file_stream,
            as_attachment=True,
            download_name=f"{directory_data["name"]}.zip",
            mimetype="application/zip"
        )

        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response
    except Exception as e:
        return f"An Error Occurred When Trying To Get Directory Data For Download {e}", 500
import base64
from flask import Flask, render_template , request, redirect, url_for
from services import github_api, arg_utils
from . import result
from markupsafe import Markup
import asyncio

@result.route("/repo-result/", methods=["GET", "POST"])
async  def repo_result():
    if request.method == "POST":
        repoOwner = str(request.form.get("repoOwner"))
        repoName = str(request.form.get("repoName"))

        try:
            repo_html = await github_api.get_github_repo_directory_tree(repoOwner, repoName)
        except Exception as e:
            return f"An Error Occurred When Trying To Receive GitHub Direstory Tree HTML {e}", 500

        if repo_html is None or repo_html == "":
            print(f"Failed To Get Data For Github Repository By Owner {repoOwner} And Name {repoName}")

            return redirect(url_for('home.index'))

        return render_template("result/result.html", repo_name=repoName, repo=Markup(repo_html))

    return redirect(url_for('home.index'))

@result.route("/view-file/<file_url_encoded>")
async def view_file(file_url_encoded):
    file_url_decoded_bytes = base64.urlsafe_b64decode(file_url_encoded.encode('utf-8'))
    file_url = file_url_decoded_bytes.decode('utf-8')

    try:
        file_data = await github_api.get_file_data(file_url)
    except Exception as e:
        return f"An Error Occurred When Trying View File {e}", 500

    if file_data is None or file_data == "":
        print(f"Failed To Get File Data {file_url} From Github Repository")

        return redirect(url_for('home.index'))

    return render_template("result/file-view.html", file_name=file_data["name"], file_path=file_data["path"], file_content=file_data["content"])
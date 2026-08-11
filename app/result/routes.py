import base64
from flask import Flask, render_template , request

from services import github_api
from . import result
from markupsafe import Markup

@result.route("/repo-result/")
def repo_result():
    repo_name = request.args.get('repo_name')

    encoded_repo_html = Markup(request.args.get("repo"))

    repo_html_decoded_bytes = base64.urlsafe_b64decode(encoded_repo_html.encode('utf-8'))
    repo_html = repo_html_decoded_bytes.decode('utf-8')

    return render_template("result/result.html", repo_name=repo_name, repo=repo_html)

@result.route("/view-file/<file_url_encoded>")
def view_file(file_url_encoded):
    file_url_decoded_bytes = base64.urlsafe_b64decode(file_url_encoded.encode('utf-8'))
    file_url = file_url_decoded_bytes.decode('utf-8')

    file_data = github_api.get_file_data(file_url)

    return render_template("result/file-view.html", file_name=file_data["name"], file_path=file_data["path"])
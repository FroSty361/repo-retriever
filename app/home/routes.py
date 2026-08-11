import base64

from flask import Flask, render_template, request, redirect, url_for
from services import github_api
from . import home

@home.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        repoOwner = str(request.form.get("repoOwner"))
        repoName = str(request.form.get("repoName"))

        repo_html = github_api.get_github_repo_data(repoOwner, repoName)

        if repo_html is None or repo_html == "":
            print(f"Failed To Get Data For Github Repository By Owner {repoOwner} And Name {repoName}")

            return render_template("home/index.html")

        repo_html_encoded_bytes = base64.urlsafe_b64encode(repo_html.encode('utf-8'))
        repo_html_encoded = repo_html_encoded_bytes.decode('utf-8')

        return redirect(url_for('result.repo_result', repo_name=repoName, repo=repo_html_encoded))

    return render_template("home/index.html")
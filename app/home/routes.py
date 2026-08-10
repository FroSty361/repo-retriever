from flask import Flask, render_template, request, redirect, url_for
from services import github_api
from . import home

@home.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        repoOwner = str(request.form.get("repoOwner"))
        repoName = str(request.form.get("repoName"))

        data = github_api.get_github_repo_data(repoOwner, repoName)

        if data is None:
            print(f"Failed To Get Data For Github Repository By Owner {repoOwner} And Name {repoName}")

            return render_template("home/index.html")

        print(data.name)

        return redirect(url_for('result.repo_result', repo_name=data.name))

    return render_template("home/index.html")
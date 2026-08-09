from flask import Flask, render_template , request

from services import github_api
from . import home

@home.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        repoOwner = str(request.form.get("repoOwner"))
        repoName = str(request.form.get("repoName"))

        data, result = github_api.get_github_repo_data(repoOwner, repoName)

        if not result:
            print(f"Failed To Get Data For Github Repository By Owner {repoOwner} And Name {repoName}")

            return render_template("home/index.html")

        return render_template("home/index.html")

    return render_template("home/index.html")
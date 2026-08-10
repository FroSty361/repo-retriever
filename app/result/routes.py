from flask import Flask, render_template , request
from . import result
from markupsafe import Markup

@result.route("/repo-result/")
def repo_result():
    repo = request.args.get("repo")

    return render_template("result/result.html", repo=Markup(repo))
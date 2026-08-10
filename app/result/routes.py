from flask import Flask, render_template , request
from . import result

@result.route("/repo-result/")
def repo_result():
    repo_name = request.args.get("repo_name")

    return render_template("result/result.html", repo_name=repo_name)
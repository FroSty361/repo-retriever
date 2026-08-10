from flask import Flask, render_template , request
from . import result

@result.route("/repo-result/")
def repo_result():
    return render_template("result/result.html", repo_name="Hi!")
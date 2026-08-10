import base64
from flask import Flask, render_template , request
from . import result
from markupsafe import Markup

@result.route("/repo-result/")
def repo_result():
    encoded_repo_html = Markup(request.args.get("repo"))

    repo_html_decoded_bytes = base64.urlsafe_b64decode(encoded_repo_html.encode('utf-8'))
    repo_html = repo_html_decoded_bytes.decode('utf-8')

    return render_template("result/result.html", repo=repo_html)
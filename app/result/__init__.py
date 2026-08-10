from flask import Flask, Blueprint

result = Blueprint("result", __name__, static_folder="../static", template_folder="../templates")

from . import routes
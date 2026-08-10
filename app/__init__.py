from flask import Flask

def create_app():
    app = Flask(__name__)

    from home import home
    app.register_blueprint(home)

    from result import result
    app.register_blueprint(result)

    return app
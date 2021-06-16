from flask_cors import CORS
from flask import Flask
import config

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.secret
    CORS(app)

    with app.app_context():
        from .frontend import frontend
        from .api import bulwark
        from .api import api

        app.register_blueprint(frontend)
        app.register_blueprint(bulwark)
        app.register_blueprint(api)

        return app

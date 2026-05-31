from flask import Flask

from .database import close_db, init_db
from .routes import register_routes


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="coursework-secret-key",
        DATABASE=None,
        UPLOAD_FOLDER=None,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    register_routes(app)

    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("数据库初始化完成")

    return app


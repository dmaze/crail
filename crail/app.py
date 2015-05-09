"""Top-level Flask application.

.. Copyright © 2015, David Maze

.. autofunction:: make_app

"""
import os

from flask import Flask
from flask.ext.assets import Environment

from .models import db, migrate
from .routes import crail_bp, crail_css, crail_js

assets = Environment()  # pylint: disable=invalid-name


def make_app():
    """Create the fully-assembled Flask application.

    This sets up the application, binding the database, migrations,
    Web assets, and the actual routes all together into one object.

    """
    app = Flask(__name__)
    app.config.from_object('crail.settings')
    app.config.from_envvar('CRAIL_SETTINGS', silent=True)

    db.init_app(app)

    # flask-migrate is super-useful, except that it depends on an
    # unpacked tree.  It doesn't look like Alembic does.  Alas!
    # At any rate, feed it the right directory so tooling works.
    migrate.init_app(app, db,
                     directory=os.path.join(os.path.dirname(__file__),
                                            'migrations'))

    assets.init_app(app)
    assets.register('crail_js', crail_js)
    assets.register('crail_css', crail_css)

    app.register_blueprint(crail_bp)

    return app

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


def make_app(config=None):
    """Create the fully-assembled Flask application.

    This sets up the application, binding the database, migrations,
    Web assets, and the actual routes all together into one object.

    If the environment variable :env:`CRAIL_SETTINGS` is set and the
    `config` parameter is :const:`None`, then the file named in the
    environment variable (if any) is loaded over the default settings.
    If `config` is not :const:`None` then that is loaded instead, and
    :env:`CRAIL_SETTINGS` is ignored.

    :param dict config: optional extra configuration parameters

    """
    app = Flask('crail')
    app.config.from_object('crail.settings')
    if config is None:
        app.config.from_envvar('CRAIL_SETTINGS', silent=True)
    else:
        app.config.update(config)

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

"""Common setup for py.test tests.

.. Copyright © 2015, David Maze

"""
import pytest

from crail.app import make_app
from crail.models import db


@pytest.fixture
def app(tmpdir):
    """py.test fixture producing a configured application.

    Data is stored in SQLite in the per-test temporary directory.

    """
    config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///{!s}/crail.db'.format(tmpdir),
        'SECRET_KEY': 'seeeekrit',
        'DEBUG': True,
        'TEST': True,
    }
    app = make_app(config)
    with app.app_context():
        db.create_all()
        db.session.commit()
    return app

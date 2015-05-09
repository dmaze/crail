"""WSGI entry point.

.. Copyright © 2015, David Maze

Pass this module to WSGI runners, like :mod:`uwsgi` or :mod:`gunicorn`.

.. autofunction:: application

"""
from .app import make_app


def application(environ, start_response):
    """WSGI entry point.

    Creates and runs the application.

    :param dict environ: WSGI environment dictionary
    :param start_response: WSGI completion callback
    :return: Iterable of content lines

    """
    app = make_app()
    return app(environ, start_response)

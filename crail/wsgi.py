'''WSGI entry point.'''
from .app import make_app


def application(environ, start_response):
    app = make_app()
    return app(environ, start_response)

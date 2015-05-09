"""Standard settings for the application.

.. Copyright © 2015, David Maze

In practice you probably want to customize this by creating a Python
settings file, and setting the :env:`CRAIL_SETTINGS` environment variable
to point at it.

The default settings store data in a :file:`crail.db` SQLite database
in the current directory.

"""

SQLALCHEMY_DATABASE_URI = 'sqlite:///crail.db'

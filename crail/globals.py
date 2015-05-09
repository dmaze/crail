"""Global state across the application.

.. Copyright © 2015, David Maze

All of these objects are available in the Flask request scope, as
thread-locals.

.. data:: current_player

   :class:`crail.models.Player` object for the current session, or
   :const:`None` if not logged in.

   Note that this is a Werkzeug local proxy holding only a weak reference
   to the object!  In particular, this means that using `current_player`
   as one side of a relationship in other :mod:`crail.models` objects
   can result in SQLAlchemy problems.  Assigning its value to a local
   variable gets around this.

"""
from flask import session
from werkzeug.local import LocalProxy

from .models import Player


def _get_current_player():
    """Get the current player object from the session."""
    player_id = session.get('player_id')
    if player_id is None:
        return None
    return Player.query.get(int(player_id))

# pylint: disable=invalid-name
current_player = LocalProxy(_get_current_player)

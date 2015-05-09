from flask import session
from werkzeug.local import LocalProxy

from .models import Player


def _get_current_player():
    player_id = session.get('player_id')
    if player_id is None:
        return None
    return Player.query.get(int(player_id))

current_player = LocalProxy(_get_current_player)

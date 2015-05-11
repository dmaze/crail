"""Unit tests for :mod:`crail.actions`.

.. Copyright © 2015, David Maze

"""
from crail.actions import draw_card, get_or_create_player
from crail.models import Card, db, Game, Player, World


def test_get_or_create_player(client):
    # This starts with an empty database
    assert Player.query.filter_by(name='me').count() == 0
    assert Player.query.count() == 0

    player = get_or_create_player('me')
    db.session.commit()
    assert player is not None
    assert player.name == 'me'

    player2 = get_or_create_player('me')
    assert player2.id == player.id
    assert player2.name == 'me'

    assert Player.query.filter_by(name='me').count() == 1
    assert Player.query.count() == 1


def test_draw_card(client):
    world = World(name='world')
    db.session.add(world)
    one = Card(event='one', world=world)
    db.session.add(one)
    two = Card(event='two', world=world)
    db.session.add(two)
    game = Game(world=world)
    db.session.add(game)
    db.session.commit()

    for _ in range(10):
        card1 = draw_card(game)
        db.session.commit()
        assert card1 == one or card1 == two
        card2 = draw_card(game)
        db.session.commit()
        assert ((card1 == one and card2 == two) or
                (card1 == two and card2 == one))

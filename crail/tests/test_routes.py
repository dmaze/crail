"""Unit tests for :mod:`crail.routes`.

.. Copyright © 2015, David Maze

"""
import json

from flask import url_for

from crail.models import Card, City, Contract, db, Good, World


def post_json(client, name, data):
    """Helper function to do a basic JSON post with JSON response."""
    response = client.post(url_for(name),
                           data=json.dumps(data),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    return response


def test_index(client):
    """Test that the index page returns something.

    This is useful because messing up the templates or JavaScript assembly
    can easily return an error.  So even though this just tests that some
    HTML comes back it is a useful defensive test.

    """
    response = client.get(url_for('crail.index'))
    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_state_initial(client):
    """Test the initial state is valid."""
    response = client.get(url_for('crail.state'))
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert response.json == {'player_id': None}


def test_login_logout(client):
    """Test a basic login/logout sequence."""
    response = post_json(client, 'crail.login', {'name': 'me'})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'games': [],
                             'worlds': []}

    response = post_json(client, 'crail.logout', {})
    assert response.json == {'player_id': None}


def test_new_game_join_game(client):
    """Test game creation, joining, leaving.

    This includes joining as a second player and making sure that you
    can see the first player's game.

    """
    world = World(name='world')
    db.session.add(world)
    db.session.commit()

    response = post_json(client, 'crail.login', {'name': 'me'})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'games': [],
                             'worlds': [{'id': 1, 'name': 'world'}]}

    response = post_json(client, 'crail.new_game', {'world': 1})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': []}

    response = post_json(client, 'crail.logout', {})
    assert response.json == {'player_id': None}

    response = post_json(client, 'crail.login', {'name': 'me'})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': []}

    response = post_json(client, 'crail.logout', {})
    assert response.json == {'player_id': None}

    response = post_json(client, 'crail.login', {'name': 'you'})
    assert response.json == {'player_id': 2,
                             'player_name': 'you',
                             'games': [{'id': 1, 'world': 'world',
                                        'players': ['me']}],
                             'worlds': [{'id': 1, 'name': 'world'}]}

    response = post_json(client, 'crail.join_game', {'game': 1})
    assert response.json == {'player_id': 2,
                             'player_name': 'you',
                             'game': 'world',
                             'money': 0,
                             'cards': []}

    response = post_json(client, 'crail.leave_game', {})
    assert response.json == {'player_id': 2,
                             'player_name': 'you',
                             'games': [{'id': 1, 'world': 'world',
                                        'players': ['me']}],
                             'worlds': [{'id': 1, 'name': 'world'}]}

    response = post_json(client, 'crail.leave_game', {})
    assert response.json == {'player_id': 2,
                             'player_name': 'you',
                             'games': [{'id': 1, 'world': 'world',
                                        'players': ['me']}],
                             'worlds': [{'id': 1, 'name': 'world'}]}


def bootstrap_world(client, world):
    """Helper function to log in and create a game.

    If `world` is :const:`None`, create one; but if you've pre-created
    a world (and other database objects) pass it in.

    """
    if world is None:
        world = World(name='world')
        db.session.add(world)
        db.session.commit()

    response = post_json(client, 'crail.login', {'name': 'me'})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'games': [],
                             'worlds': [{'id': 1, 'name': 'world'}]}

    response = post_json(client, 'crail.new_game', {'world': world.id})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': []}


def test_gain_money(client):
    """Test free-standing "gain money"."""
    bootstrap_world(client, world=None)

    response = post_json(client, 'crail.gain_money', {'amount': 5})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 5,
                             'cards': []}


def test_spend_money(client):
    """Test spending money."""
    bootstrap_world(client, world=None)

    response = post_json(client, 'crail.spend_money', {'amount': 17})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': -17,
                             'cards': []}


def test_draw_discard_one_event(client):
    """Test format of event card and discard call."""
    world = World(name='world')
    db.session.add(world)
    card = Card(number=123, event='oh noes!', world=world)
    db.session.add(card)
    db.session.commit()

    bootstrap_world(client, world)

    response = post_json(client, 'crail.draw', {})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': [{'id': 1, 'number': 123,
                                        'event': 'oh noes!'}]}

    response = post_json(client, 'crail.discard', {'card': 2})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': [{'id': 1, 'number': 123,
                                        'event': 'oh noes!'}]}

    response = post_json(client, 'crail.discard', {'card': 1})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': []}

    response = post_json(client, 'crail.draw', {})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 0,
                             'cards': [{'id': 1, 'number': 123,
                                        'event': 'oh noes!'}]}


def test_draw_complete_two_contracts(client):
    """Test format of contract card and complete card."""
    # This has a lot of setup!
    world = World(name='world')
    stuff = Good(name='stuff')
    things = Good(name='things')
    cruft = Good(name='cruft')
    here = City(name='here', produces=[stuff], world=world)
    there = City(name='there', produces=[things], world=world)
    elsewhere = City(name='elsewhere', produces=[cruft], world=world)
    contract1 = Contract(good=stuff, city=there, amount=5)
    contract2 = Contract(good=things, city=elsewhere, amount=7)
    contract3 = Contract(good=cruft, city=here, amount=9)
    card1 = Card(number=1, contracts=[contract1, contract2, contract3],
                 world=world)
    card2 = Card(number=2, event='FOO!', world=world)

    db.session.add_all([world,
                        stuff, things, cruft,
                        here, there, elsewhere,
                        contract1, contract2, contract3,
                        card1, card2])
    db.session.commit()

    bootstrap_world(client, world)

    # Consciously draw twice; we should get both cards
    response = post_json(client, 'crail.draw', {})
    response = post_json(client, 'crail.draw', {})
    assert response.json['player_id'] == 1
    assert response.json['player_name'] == 'me'
    assert response.json['game'] == 'world'
    assert response.json['money'] == 0
    assert len(response.json['cards']) == 2
    res_cards = sorted(response.json['cards'], key=lambda d: d['id'])
    assert res_cards[0]['id'] == 1
    assert res_cards[0]['number'] == 1
    res_contracts = sorted(res_cards[0]['contracts'], key=lambda d: d['id'])
    assert res_contracts == [
        {'id': 1, 'good': 'stuff', 'city': 'there', 'amount': 5},
        {'id': 2, 'good': 'things', 'city': 'elsewhere', 'amount': 7},
        {'id': 3, 'good': 'cruft', 'city': 'here', 'amount': 9}
    ]
    assert res_cards[1] == {'id': 2, 'number': 2, 'event': 'FOO!'}

    response = post_json(client, 'crail.complete', {'contract': 2})
    assert response.json == {'player_id': 1,
                             'player_name': 'me',
                             'game': 'world',
                             'money': 7,
                             'cards': [{'id': 2, 'number': 2,
                                        'event': 'FOO!'}]}

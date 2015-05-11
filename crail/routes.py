"""Flask blueprint for the application proper.

.. Copyright © 2015, David Maze

This module only contains the URL-routing logic.  While it assumes that,
for instance, a database object is in scope, actually setting that up is
done in :func:`crail.app.make_app`.

.. autodata:: crail_bp
.. autodata:: crail_js
.. autodata:: crail_css

"""
from .actions import draw_card, get_or_create_player
from .globals import current_player
from .models import Card, Contract, db, Game, World
from flask import abort, Blueprint, current_app, jsonify, render_template, \
    request, session
from flask.ext.assets import Bundle


#: Flask blueprint for crayon-rails handlers.
crail_bp = Blueprint('crail', __name__)

#: Flask-Assets bundle for :data:`crail_bp` JavaScript.
crail_js = Bundle('bower_components/jquery/dist/jquery.js',
                  'bower_components/bootstrap/dist/js/bootstrap.js',
                  'bower_components/underscore/underscore.js',
                  'bower_components/js-cookie/src/js.cookie.js',
                  'crail.js',
                  filters='rjsmin', output='gen/packed.js')

#: Flask-Assets bundle for :data:`crail_bp` CSS.
crail_css = Bundle('bower_components/bootstrap/dist/css/bootstrap.css',
                   'bower_components/bootstrap/dist/css/bootstrap-theme.css',
                   filters='cssmin', output='gen/packed.css')


@crail_bp.route('/')
def index():
    """Return the top-level HTML page."""
    return render_template('index.html')


def player_state():
    """Get the current state as a JSON Flask response.

    Most calls will return this, even if it's a little redundant.
    This always includes enough state for the UI to take some action.
    The return is a JSON object, with the following keys:

    `player_id`
      Always present; the numeric player ID if logged in, or ``null``
    `player_name`
      The player's name, if logged in
    `games`
      If logged in but not in a game, a list of current games, each
      with `id`, `world` (name), and `players` (list of names)
    `worlds`
      If logged in but not in a game, a list of available worlds for
      new games, each with `id` and `name`
    `game`
      If logged in and in a game, the name of the world
    `money`
      If logged in and in a game, the amount of money the current player
      has
    `cards`
      If logged in and in a game, the list of cards the current player has.
      Each is a dictionary with `id`, `number` (printed on the card, if
      available), `event` (text, if the card is an event card), and
      `contracts`.  Each contract in turn has `id`, `good`, `city`, and
      `amount`.

    """
    response = {'player_id': None}

    # (Remember current_player will always be a proxy and will never be
    # None, but it could be a proxy to None)
    if not current_player:
        return jsonify(response)

    response['player_id'] = current_player.id
    response['player_name'] = current_player.name

    if not current_player.game:
        response['games'] = [{
            'id': game.id,
            'world': game.world.name,
            'players': [player.name for player in game.players],
        } for game in Game.query.order_by('id')]
        response['worlds'] = [{
            'id': world.id,
            'name': world.name,
        } for world in World.query.order_by('id')]
        return jsonify(response)

    response['game'] = current_player.game.world.name
    response['money'] = current_player.money

    def card_to_dict(card):
        """Translate a card to a JSON dictionary."""
        jcard = {'id': card.id}
        if card.number:
            jcard['number'] = card.number
        if card.event:
            jcard['event'] = card.event
        if card.contracts:
            jcard['contracts'] = [{'id': contract.id,
                                   'good': contract.good.name,
                                   'city': contract.city.name,
                                   'amount': contract.amount}
                                  for contract in card.contracts]
        return jcard

    response['cards'] = [card_to_dict(card) for card in current_player.cards]

    return jsonify(response)


@crail_bp.route('/api/state')
def state():
    """Retrieve the current state."""
    return player_state()


@crail_bp.route('/api/login', methods=['POST'])
def login():
    """Log in to the system.

    This is a purely assertion-based login scheme: any name will be
    accepted with no further credentials.

    The request body is a JSON object with a `name` key giving the
    name to log in as.

    """
    args = request.get_json()
    name = args.get('name', None)
    if not name:
        abort(400)  # bad request

    # Win, find or create a player
    player = get_or_create_player(name)
    db.session.commit()

    session['player_id'] = player.id
    return player_state()


@crail_bp.route('/api/logout', methods=['POST'])
def logout():
    """Log out of the system."""
    if 'player_id' in session:
        del session['player_id']
    return player_state()


@crail_bp.route('/api/game/join', methods=['POST'])
def join_game():
    """Join a game.

    The request body is a JSON object with a key `game`, with the numeric
    game ID.  You must be logged in already.

    """
    if not current_player:
        abort(400)

    args = request.get_json()
    game_id = args.get('game', None)
    if game_id is None:
        abort(400)

    game = Game.query.get(game_id)
    if game is None:
        abort(400)

    current_player.game = game
    db.session.commit()
    return player_state()


@crail_bp.route('/api/game/leave', methods=['POST'])
def leave_game():
    """Leave a game.

    You must be logged in.  This is a no-op (but a successful one) if
    you are not currently in a game.

    """
    if not current_player:
        abort(400)
    current_player.game = None
    db.session.commit()
    return player_state()


@crail_bp.route('/api/game/new', methods=['POST'])
def new_game():
    """Start a new game.

    The request body is a JSON object with a `world` parameter holding
    the numeric world ID.  You must be logged in already, and will
    automatically join the new game.

    """
    if not current_player:
        abort(400)

    args = request.get_json()
    world_id = args.get('world', None)
    if world_id is None:
        abort(400)

    world = World.query.get(world_id)
    if world is None:
        abort(400)

    game = Game(world=world)
    db.session.add(game)
    current_player.game = game
    db.session.commit()
    return player_state()


@crail_bp.route('/api/gain', methods=['POST'])
def gain_money():
    """Increase the amount of money you have.

    The request body is a JSON dictionary with a key `amount`.  You must
    be logged in.

    """
    if not current_player:
        abort(400)

    args = request.get_json()
    amount = args.get('amount', None)
    if amount is None:
        abort(400)

    current_player.money += amount
    db.session.commit()
    return player_state()


@crail_bp.route('/api/spend', methods=['POST'])
def spend_money():
    """Decrease the amount of money you have.

    The request body is a JSON dictionary with a key `amount`.  You must
    be logged in.

    This and :func:`gain_money` are identical except for the sign.  Gaining
    negative money is the same as this.

    """
    if not current_player:
        abort(400)

    args = request.get_json()
    amount = args.get('amount', None)
    if amount is None:
        abort(400)

    current_player.money -= amount
    db.session.commit()
    return player_state()


@crail_bp.route('/api/draw', methods=['POST'])
def draw():
    """Draw a card.

    You must be logged in.  The card is added to your current cards list
    and returned.

    This endpoint currently has no game knowledge.  You will always get
    exactly one more card if it is there to be drawn.  If it is an event
    card this will not draw another; if you already have "enough" cards
    this will not prevent you from continuing to draw.

    """
    player = current_player._get_current_object()
    if not player:
        abort(400)

    card = draw_card(player.game)
    player.cards.append(card)
    db.session.commit()
    return player_state()


@crail_bp.route('/api/discard', methods=['POST'])
def discard():
    """Discard a card.

    The request body is a JSON object with a key `card` with the
    numeric card ID.  You must be logged in.  The card is removed from
    your current cards list.

    This call "completes an event", or is one part of "flushing
    contracts".  In principle this and :func:`gain_money` can "deliver
    a contract", though :func:`complete` is a better way to do it.

    """
    player = current_player._get_current_object()
    if not player:
        abort(400)

    args = request.get_json()
    card_id = args.get('card', None)
    if card_id is None:
        abort(400)

    card = Card.query.get(card_id)
    if card is not None and card in player.cards:
        player.cards.remove(card)
        db.session.commit()
    return player_state()


@crail_bp.route('/api/complete', methods=['POST'])
def complete():
    """Complete a contract.

    The request body is a JSON object with a key `contract` with the
    numeric contract ID.  You must be logged in and in a game.  This
    adds the amount of the contract to your money holding and discards
    the card, but does not draw a new one to replace it.

    """
    player = current_player._get_current_object()
    if not player:
        current_app.logger.error('complete: no current player')
        abort(400)

    args = request.get_json()
    contract_id = args.get('contract', None)
    if contract_id is None:
        current_app.logger.error('complete: no contract ID')
        abort(400)

    contract = Contract.query.get(contract_id)
    for card in contract.cards:
        if player in card.players:
            player.money += contract.amount
            player.cards.remove(card)
    db.session.commit()
    return player_state()

from .actions import draw_card, get_or_create_player
from .globals import current_player
from .models import Card, Contract, db, Game, Player, World
from flask import Blueprint, abort, jsonify, render_template, request, \
    session
from sqlalchemy.orm.exc import NoResultFound


crail_bp = Blueprint('crail', __name__)


@crail_bp.route('/')
def index():
    return render_template('index.html')


def player_state():
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
        d = {'id': card.id}
        if card.number:
            d['number'] = card.number
        if card.event:
            d['event'] = card.event
        if card.contracts:
            d['contracts'] = [{'id': contract.id,
                               'good': contract.good.name,
                               'city': contract.city.name,
                               'amount': contract.amount}
                              for contract in card.contracts]
        return d

    response['cards'] = [card_to_dict(card) for card in current_player.cards]

    return jsonify(response)


@crail_bp.route('/api/state')
def state():
    return player_state()


@crail_bp.route('/api/login', methods=['POST'])
def login():
    args = request.get_json()
    name = args.get('name', None)
    if not name:
        abort(400)  # bad request

    # Win, find or create a player
    player = get_or_create_player(name)
    session['player_id'] = player.id

    db.session.commit()
    return player_state()


@crail_bp.route('/api/logout', methods=['POST'])
def logout():
    if 'player_id' in session:
        del session['player_id']
    return player_state()


@crail_bp.route('/api/game/join', methods=['POST'])
def join_game():
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
    if not current_player:
        abort(400)
    current_player.game = None
    db.session.commit()
    return player_state()


@crail_bp.route('/api/game/new', methods=['POST'])
def new_game():
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
    player = current_player._get_current_object()
    if not player:
        abort(400)

    card = draw_card(player.game)
    player.cards.append(card)
    db.session.commit()
    return player_state()


@crail_bp.route('/api/discard', methods=['POST'])
def discard():
    player = current_player._get_current_object()
    if not player:
        abort(400)

    args = request.get_json()
    card_id = args.get('card', None)
    if card_id is None:
        abort(400)

    card = Card.query.get(card_id)
    player.cards.remove(card)
    db.session.commit()
    return player_state()
    

@crail_bp.route('/api/complete', methods=['POST'])
def complete():
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

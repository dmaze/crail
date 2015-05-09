'''UI-agnostic actions.'''
from random import choice

from .models import Card, db, PlayedCard, Player

def get_or_create_player(name):
    '''Get a player with a given name.

    If there is no existing player, create a new one.  Does not implicitly
    commit, but does record the new player in the session.

    :param str name: name of the player
    :return: :class:`crail.models.Player`

    '''
    try:
        return Player.query.filter_by(name=name).one()
    except NoResultFound:
        player = Player(name=name, money=0)
        db.session.add(player)
        return player


def draw_card(game):
    '''Draw a card for the current game.

    Adds the card to the played-cards table (and may clear that table out
    to reshuffle it), so intrinsically causes a mutation.

    '''
    cards = (Card.query
             .filter_by(world=game.world)
             .filter(~Card.played_cards.any(PlayedCard.game==game))
             .all())
    if not cards:
        # reshuffle
        PlayedCard.query.filter_by(game=game).delete()
        cards = Card.query.filter_by(world=game.world).all()
    card = choice(cards)
    pc = PlayedCard(game=game, card=card)
    db.session.add(pc)
    return card

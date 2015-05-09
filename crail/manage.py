#!/usr/bin/env python3
'''Debug server.'''
import sys
import yaml
from .app import make_app
from .models import Card, City, Contract, Good, World, db
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
from flask.ext.script.commands import InvalidCommand
from sqlalchemy.orm.exc import NoResultFound


manager = Manager(make_app)
manager.add_command('db', MigrateCommand)


@manager.option('filename')
def game(filename):
    """Import a YAML file of game data."""
    with open(filename, 'r') as f:
        contents = yaml.safe_load(f)

    world_name = contents['name']
    try:
        world = World.query.filter_by(name=world_name).one()
    except NoResultFound:
        world = World(name=world_name)
        db.session.add(world)

    for city_name, city_produces in contents['cities'].items():
        try:
            city = City.query.filter_by(name=city_name, world=world).one()
        except NoResultFound:
            city = City(name=city_name, world=world)
            db.session.add(city)

        for good_name in city_produces:
            try:
                good = Good.query.filter_by(name=good_name).one()
            except NoResultFound:
                good = Good(name=good_name)
                db.session.add(good)
            city.produces.append(good)

    for card_num, card_data in enumerate(contents['cards']):
        if 'number' in card_data:
            card_num = card_data['number']
        try:
            card = Card.query.filter_by(number=card_num, world=world).one()
        except NoResultFound:
            card = Card(number=card_num, world=world)
            db.session.add(card)
        card.event = card_data.get('event')
        for contract_data in card_data.get('contracts', []):
            try:
                good = Good.query.filter_by(name=contract_data[0]).one()
            except NoResultFound:
                raise InvalidCommand('Good {} does not exist'
                                     .format(contract_data[0]))
            try:
                city = City.query.filter_by(name=contract_data[1],
                                            world=world).one()
            except NoResultFound:
                raise InvalidCommand('City {} does not exist'
                                     .format(contract_data[1]))
            try:
                contract = Contract.query.filter_by(good=good, city=city).one()
            except NoResultFound:
                contract = Contract(good=good, city=city)
            contract.amount = contract_data[2]
            card.contracts.append(contract)

    db.session.commit()


def main():
    try:
        manager.run()
    except InvalidCommand as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

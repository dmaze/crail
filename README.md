Crayon Rails Assistant
======================

This is a simple Web assistant for "crayon rails" board games,
generally Mayfair Games's
[Empire Builder](http://en.wikipedia.org/wiki/Empire_Builder_%28board_game%29)
and its many variants.  This replicates only the "accounting" aspect
of the game, more to protect my already-overloved
[Iron Dragon](http://www.boardgamegeek.com/boardgame/130/iron-dragon)
contract cards from complete disintegration.

Ettiquette
----------

The set of contract cards you hold is generally public; the amount of
money you have is generally not.  Please share with your fellow
players when you do deliver a contract and for how much, even if
contract cards aren't being physically passed around.  Especially if
you draw an event card, make sure the entire game is aware of it.

Setup
-----

This package is not especially self-contained.  You will need to do
the following:

* Install the [Bower](http://bower.io) JavaScript package manager.

* Run ``bower install`` to bring in client-side dependencies.

* Create a Python 3 virtual environment, and ``pip install`` this
  package into it.

* Create a local settings file.  It needs to contain at least::

    SQLALCHEMY_DATABASE_URI = '...'
    SECRET_KEY = '...'

  The [SQLAlchemy](http://sqlalchemy.org/) backend URI can be any supported
  URI; for instance, ``sqlite:////tmp/crail.db``.  The secret key should
  be a string of actually-random bytes.

* Set an environment variable ``CRAIL_SETTINGS`` to the absolute path
  to the local settings file.

* Run ``crail_manage db upgrade``, which will create the initial
  (empty) database.

* Create a world YAML file as described below, and run ``crail_manage
  game mygame.yaml`` to load it into the database.

* Run ``crail_manage runserver`` to run a local debug server, or
  deploy this on a real server like [GUnicorn](http://gunicorn.org/)
  or [uwsgi](http://uwsgi.rtfd.org/).

* Point your friends' smart phone browsers at your laptop.

Worlds
------

You need to manually enter some information from your crayon-rails
game.  (I almost certainly cannot distribute this for copyright
reasons.)  In a text editor create a YAML file that looks like the
following::

    name: Boston Rails
    cities:
      Boston: [Baked beans]
      Cambridge: [Electronics]
      Somerville: [Coffee, Beer]
      Everett: [Beer]
      Braintree: [Brains]
      Lexington: [Minutemen]
    cards:
      - contracts:
          - [Brains, Cambridge, 15]
          - [Coffee, Everett, 12]
          - [Electronics, Boston, 5]
      - event: Evacuation Day (half rate within 5 of Boston)

There can be any number of cities, contract, and event cards, and you
can freely mix contracts and events.  Any text you enter for an event
will be displayed verbatim in players' browsers.  The "cities" listing
includes a list of goods each city produces.

The load process enforces that a contract card has a known city and
good, but does not necessarily strongly tie them to the same game --
it is probably possible if you have the right games entered to enter a
contract for dragons (from Iron Dragon) to Newcastle (from either
British Rails or Eurorails) in what is ostensibly an India Rails game.

On security and persistence
---------------------------

There is consciously no real security in this application: anyone who
can access it can enter any name and join any game.  If you're running
this on a private server on your home wifi, this is probably good
enough.  Conversely, you can peek at someone else's cards (and money)
by logging out and entering their name in the login page.

On the flip side, all of the information in this application is stored
in the database.  Some key information (notably the player ID) is
stored in an encrypted session cookie, but logging in from a new
browser can recreate this easily enough.  If you have a power blip
that takes out everybody's laptops, you should not lose game state.

On the third hand, there's no good way to end or delete a game right
now.  If you're using an SQLite file database, deleting and reloading
it is a fine way to go.

TODO
----

I've thought about...

* Better game management: end a game, delete a game, and so on 

* Make events global (until the drawing player dismisses them)

* Add a detailed description to events

* Keep a fixed number of (non-event) cards in hand

* "Flush contracts" option

* Public contracts

* Directly inspect other players' cards

* Direct player-to-player payments (e.g. for rail use fees)

* "End turn" button; notification that it is your turn now;
  auto-expiration of events

* Separate player identity from player-in-game state (so you can
  usefully have multiple live games for the same player)

* Make actions undoable, and remove in-app confirmations

Thoughts and goals
------------------

The real game I want an online assistant for is 18xx, where the most
time-consuming parts of the game are finding an optimal path through a
graph and looking at the past financial performance of a company, both
of which are jobs computers are good at.

This project was also an attempt to stitch together a handful of
common technologies to build a simple Web application.  I went from
nothing to an essentially working application in about 15 hours' time.
I'm not sure if it's a bad sign that it took me 15 hours to build such
a simple application, or a good sign that I could get a working Python
(Flask), HTML, JavaScript (JQuery), and CSS (Bootstrap) application up
and running in only 15 hours, or a bad sign that I spent an entire
weekend coding.

I have learned that Flask is a pretty good framework, and that many of
the Flask plugins solve obvious problems.  I have learned that Python
3 isn't that different from Python 2, though mixing and matching is a
worst-of-both-worlds situation.  I have also learned that the "Web
asset" land (of node.js and bower and grunt) is still essentially
totally separate from the Python application land (of setuptools and
pip) and it's very hard to write an application that's not dependent
on the public Internet and also doesn't need multiple concurrent build
systems.

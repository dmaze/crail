(function() {

    var currentPlayerId = null;
    var currentPlayerName = null;
    var currentState = null;

    var cardById = function(cardId) {
        if (!currentState) return null;
        return _.findWhere(currentState.cards, {id: cardId});
    };
    
    var clickableListItem = function() {
        return $('<a>').addClass('list-group-item').attr('href', '#');
    };
    
    var resetUiFromState = function(state) {
        currentState = state;
        currentPlayerId = state.player_id;
        currentPlayerName = state.player_name;
        $('#name-control').text(currentPlayerName || 'Me');

        // No current player?  Only show login page
        if (!currentPlayerId) {
            $('#game-name-control').text('Crail');
            $('#user-control').addClass('hidden');
            $('#login-page').removeClass('hidden');
            $('#game-page').addClass('hidden');
            $('#world-page').addClass('hidden');
            $('#main-page').addClass('hidden');
            return;
        }
        $('#user-control').removeClass('hidden');
        $('#login-page').addClass('hidden');

        // No current game?  Pick one
        // New game/pick world acts as a subpage of this, and if
        // we come back here we will always restart from "pick an
        // existing game"
        if (!state.game) {
            $('#game-name-control').text('Crail');
            setGameList(state.games);
            setWorldList(state.worlds);
            $('#game-page').removeClass('hidden');
            $('#world-page').addClass('hidden');
            $('#main-page').addClass('hidden');
            return;
        }

        // Otherwise we are playing a real game.
        $('#game-name-control').text(state.game);
        $('#game-page').addClass('hidden');
        $('#world-page').addClass('hidden');
        $('#main-page').removeClass('hidden');

        $('#money').val(state.money);
        setCardList(state.cards);
    };

    var setGameList = function(games) {
        $('#game-list > a.game-choice').remove();
        var newItem = $('#game-list > #new-game-action').detach();
        _.each(games, function(game) {
            var item = clickableListItem()
                .addClass('game-choice')
                .data('gameId', game.id)
                .append($('<b>').text(game.world))
                .append($('<span>').text(' ' + game.players.join(', ')))
            $('#game-list').append(item);
        });
        $('#game-list').append(newItem);
    };

    var setWorldList = function(worlds) {
        $('#world-list > a.world-choice').remove();
        var backItem = $('#world-list > #old-game-action').detach();
        _.each(worlds, function(world) {
            var item = clickableListItem()
                .addClass('world-choice')
                .data('worldId', world.id)
                .append($('<b>').text(world.name));
            $('#world-list').append(item);
        });
        $('#world-list').append(backItem);
    };

    /**
     * Add markup describing an event to some DOM element.
     *
     * @param card  Card containing an event
     * @param item  DOM element to append to
     */
    var describeEvent = function(card, item) {
        item.append($('<span>')
                    .addClass('glyphicon')
                    .addClass('glyphicon-alert'))
            .append('\xa0' + card.event);
    };

    /** Add markup describing a contract to some DOM element.
     *
     * @param contract  The contract to describe
     * @param item      DOM element to append to
     */
    var describeContract = function(contract, item) {
        item.append($('<span>')
                    .addClass('glyphicon')
                    .addClass('glyphicon-transfer'))
            .append('\xa0' + contract.good + ' to ' +
                    contract.city + ' for ' + contract.amount);
    };

    var describeCard = function(card, item) {
        if (card.event) {
            describeEvent(card, item);
            item.append($('<br>'));
        }
        _.each(card.contracts || [], function(contract) {
            describeContract(contract, item);
            item.append($('<br>'));
        });
    };
    
    var setCardList = function(cards) {
        // Try hard to avoid making a change if we don't need to
        var drawCardAction = null;
        var cardIds = new Array();

        // Add new cards (avoiding cards that are already in the UI)
        _.each(cards, function(card) {
            cardIds.push(card.id);
            
            // Is this card already in the UI?
            if ($('#cards-list > a')
                .filter(function() {
                    return $(this).data('cardId') === card.id;
                })
                .size() > 0) {
                return;
            }

            // We're about to append something; save trailers if needed
            if (!drawCardAction) {
                drawCardAction = $('#cards-list > #draw-card-action').remove();
            }

            var hasContracts = false;
            var item = clickableListItem()
                .data('cardId', card.id);
            describeCard(card, item);
            if (card.contracts) {
                item.addClass('contract-card')
                    .attr('data-toggle', 'modal')
                    .attr('data-target', '#contract-modal');
            } else {
                item.addClass('simple-card')
                    .attr('data-toggle', 'modal')
                    .attr('data-target', '#discard-modal');
            }
            $('#cards-list').append(item);
        });
        if (drawCardAction) {
            $('#cards-list').append(drawCardAction);
        }

        // Similarly go through the list of existing cards and remove
        // any that are gone
        $('#cards-list > *').filter(function() {
            return (($(this).hasClass('simple-card') ||
                     $(this).hasClass('contract-card')) &&
                    !_.contains(cardIds, $(this).data('card-id')));
        }).remove();
    };

    var postJson = function(url, data, options) {
        options = _.extend(options || {}, {
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            headers: {
                'X-CSRFToken': $.cookie('_csrf_token')
            },
            dataType: 'json'
        });
        return $.ajax(url, options);
    };

    $('#login-submit').on('click', function() {
        var name = $('#login-name').val();
        postJson('api/login', {
            name: name
        }).then(resetUiFromState);
    })

    $('#leave-game-action').on('click', function() {
        postJson('api/game/leave', {}).then(resetUiFromState);
    });
    
    $('#logout-action').on('click', function() {
        postJson('api/logout', {}).then(resetUiFromState);
    });

    $('#game-list').on('click', '.game-choice', function() {
        // JQuery sets this to the world-choice element
        postJson('api/game/join', {
            game: $(this).data('game-id')
        }).then(resetUiFromState);
    });
    
    $('#new-game-action').on('click', function() {
        $('#game-page').addClass('hidden');
        $('#world-page').removeClass('hidden');
    });

    $('#world-list').on('click', '.world-choice', function() {
        // JQuery sets this to the world-choice element
        postJson('api/game/new', {
            world: $(this).data('world-id')
        }).then(resetUiFromState);
    });
    
    $('#old-game-action').on('click', function() {
        $('#world-page').addClass('hidden');
        $('#game-page').removeClass('hidden');
    });

    $('#gain-action').on('click', function() {
        postJson('api/gain', {
            amount: parseInt($('#gain-amount').val())
        }).then(resetUiFromState);
    });

    $('#spend-action').on('click', function() {
        postJson('api/spend', {
            amount: parseInt($('#spend-amount').val())
        }).then(resetUiFromState);
    });

    $('#cards-list').on('click', '#draw-card-action', function() {
        postJson('api/draw', {}).then(resetUiFromState);
    });

    $('#cards-list').on('click', '.simple-card', function() {
        $('#discard-id').text($(this).data('card-id'));
        $('#discard-description').empty().append($(this).text());
    });

    $('#discard-action').on('click', function() {
        postJson('api/discard', {
            card: parseInt($('#discard-id').text())
        }).then(resetUiFromState);
    });

    $('#cards-list').on('click', '.contract-card', function() {
        var cardId = parseInt($(this).data('card-id'));
        $('#contract-card-id').text(cardId);
        var card = cardById(cardId);
        $('#contract-list > .contract-select').remove();
        var discard = $('#contract-list > #contract-discard').detach();
        _.each(card.contracts || [], function(contract) {
            var item = clickableListItem()
                .addClass('contract-select')
                .data('contractId', contract.id);
            describeContract(contract, item);
            $('#contract-list').append(item);
        });

        $('#contract-list').append(discard);
        discard.data('cardId', cardId);
    });

    $('#contract-list').on('click', '.contract-select', function() {
        $('#contract-confirm-id').text($(this).data('contractId'));
        $('#contract-confirm-description').empty().append($(this).text());
        
        // We will manually advance modals here
        $('#contract-modal').modal('hide');
        $('#contract-confirm-modal').modal('show');
    });

    $('#contract-confirm-cancel').on('click', function() {
        // Manually rewind modals; contract-modal should still be set up
        $('#contract-confirm-modal').modal('hide');
        $('#contract-modal').modal('show');
    });

    $('#contract-confirm-action').on('click', function() {
        postJson('api/complete', {
            contract: parseInt($('#contract-confirm-id').text())
        }).then(resetUiFromState);
    });

    $('#contract-list').on('click', '#contract-discard', function() {
        var cardId = parseInt($(this).data('cardId'));
        $('#contract-discard-id').text(cardId);
        var card = cardById(cardId);
        if (!card) {
            console.error('discard modal: not holding card!', cardId,
                          currentState);
            return;  // not touching modals
        }
        $('#contract-discard-description').empty();
        describeCard(card, $('#contract-discard-description'));

        $('#contract-modal').modal('hide');
        $('#contract-discard-modal').modal('show');
    });
    
    $('#contract-discard-cancel').on('click', function() {
        // Manually rewind modals; contract-modal should still be set up
        $('#contract-discard-modal').modal('hide');
        $('#contract-modal').modal('show');
    });

    $('#contract-discard-action').on('click', function() {
        postJson('api/discard', {
            card: parseInt($('#contract-discard-id').text())
        }).then(resetUiFromState);
    });
    
    $.ajax('api/state', {
        'dataType': 'json',
    }).then(resetUiFromState);
    
})();

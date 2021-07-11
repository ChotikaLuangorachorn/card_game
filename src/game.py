from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from random import shuffle
from .model.game import Card, GameInDB
from .model.user import User
from .database import users_db, game_db
from .authentication import *
from copy import deepcopy
from typing import List

game_router = APIRouter(
    prefix='/game',
    tags = ['game'],
    responses = {status.HTTP_404_NOT_FOUND: {'message': 'Not found'}}
)

def start_new_game(game_db, user: User):
    card_number = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
    shuffle(card_number)
    card_model = []
    card_id = 1
    for num in card_number:
        card = Card(id=card_id, card_value = num)
        card_model.append(card)
        card_id += 1

    game_db.update({user.username: {
        'click': 0,
        'scores': game_db[user.username]['scores'],
        'cards' : card_model,
        'fist_open_card': None,
        'second_open_card': None,
        'opened_cards' : []
    }})

def temporarily_hide_card_value(cards: List[Card]):
    temp_cards = deepcopy(cards)
    for card in temp_cards:
        if not card.is_shown and not card.is_correct:
            card.card_value = "??"
    return temp_cards

def open_and_check_card(card_id: int,user: User,  game_info: GameInDB):
    is_match_first_card = game_info.is_match_first_card
    cards = game_info.cards
    card_id = card_id - 1
    selected_card = cards[card_id]
    opened_cards = game_info.opened_cards
    game_detail = game_db[user.username]

    if selected_card.is_shown or selected_card in opened_cards: # Case 1: the selected card is already shown.
        temp_cards = temporarily_hide_card_value(cards)
        return {"cards": temp_cards}

    game_detail['click'] += 1

    if is_match_first_card: # Case 2: open fist card for matching
        
        selected_card.is_shown = True
        game_detail['is_match_first_card'] = False
        if len(opened_cards) != 0:
            count_correct = 0
            for card in opened_cards[-2:]:
                if (not card.is_correct):
                    cards[card.id - 1].is_shown = False
                    count_correct += 1
            if count_correct != 0:
                opened_cards = opened_cards[:-count_correct]
        
        temp_cards = temporarily_hide_card_value(cards)
        opened_cards += [selected_card]
        game_detail['cards'] =  cards

        
    else: # Case 3: open second card for matching
        selected_card.is_shown = True
        latest_card = opened_cards[-1]
        cards[latest_card.id - 1].is_shown = True
        

        # Case 3.1: the second card value is equal to the first card value.
        if latest_card.card_value == selected_card.card_value:
            latest_card.is_correct = True
            selected_card.is_correct = True
            cards[latest_card.id - 1].is_correct = True
            temp_cards = temporarily_hide_card_value(cards)
            opened_cards+= [selected_card]
            # game_detail['opened_cards'] = opened_cards

            # corrected all
            if len(opened_cards) == 12:
                count_correct = 0
                for card in opened_cards:
                    if not card.is_correct:
                        break
                    count_correct += 1
                if count_correct == 12:
                    game_detail['scores'] += [game_detail['click']]
                    print(game_detail['scores'])
           
        
        # Case 3.2: the second card value is not equal to the first card value.
        else:
            opened_cards+= [selected_card]
            temp_cards = temporarily_hide_card_value(cards)

        game_detail['is_match_first_card'] = True
    game_detail['cards'] =  cards
    game_detail['opened_cards']= opened_cards

    return {"cards": temp_cards}

# -------------------- router --------------------
@game_router.get('/new_game')
async def new_game(current_user: User = Depends(get_current_active_user)):
    start_new_game(game_db, current_user)

    return {"message": "new game ready"}

@game_router.get('/play_game')
async def play_game(current_user: User = Depends(get_current_active_user)):
    game_info = GameInDB(**game_db[current_user.username])
    cards = game_info.cards
    if cards == []:
        start_new_game(game_db, current_user)
        game_info = GameInDB(**game_db[current_user.username])
        cards = game_info.cards
    temp_cards = temporarily_hide_card_value(cards)
    return {"cards": temp_cards}

@game_router.get('/open_card/{card_id}')
async def open_card(card_id: int, current_user: User = Depends(get_current_active_user)):
    if card_id < 1 or card_id > 12:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Invalid card id")
    game_info = GameInDB(**game_db[current_user.username])
    cards = game_info.cards
    if cards == []:
        start_new_game(game_db, current_user)
        game_info = GameInDB(**game_db[current_user.username])
    return open_and_check_card(card_id, current_user,game_info)

@game_router.get('/click')
async def open_card(current_user: User = Depends(get_current_active_user)):
    game_info = GameInDB(**game_db[current_user.username])
    return {"click": game_info.click}

@game_router.get('/scores/all')
async def open_card(current_user: User = Depends(get_current_active_user)):
    game_info = GameInDB(**game_db[current_user.username])
    return {"scores": game_info.scores}

@game_router.get('/scores/my_latest')
async def open_card(current_user: User = Depends(get_current_active_user)):
    game_info = GameInDB(**game_db[current_user.username])
    scores = game_info.scores
    if len(scores) == 0:
        return {"latest_score": scores}
    return {"latest_score": game_info.scores[-1]}

@game_router.get('/scores/my_best')
async def open_card(current_user: User = Depends(get_current_active_user)):
    game_info = GameInDB(**game_db[current_user.username])
    scores = game_info.scores
    if len(scores) == 0:
        return {"best_score": scores}
    return {"best_score": min(scores)}
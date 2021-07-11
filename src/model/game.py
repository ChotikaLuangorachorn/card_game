from pydantic import BaseModel, PositiveInt, conint, validators
from typing import Optional, List
class Card(BaseModel):
    id: int
    card_value: str
    is_shown: Optional[bool] = False
    is_correct: Optional[bool] = False

class GameInDB(BaseModel):
    click: Optional[int] = 0
    scores: List[int] = []
    cards: List[Card] = []
    is_match_first_card: Optional[bool] = True
    opened_cards: List[Card] = []
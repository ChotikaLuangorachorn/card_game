import unittest
from src.model.game import Card
from src.game import *
from src.authentication import *
class TestCardGame(unittest.TestCase):

    def test_temporarily_hide_card_value(self):
        cards = [
            Card(id=1, card_value="2", is_shown=True),
            Card(id=2, card_value="1", is_shown=False),
            Card(id=3, card_value="3", is_shown=False),
            Card(id=4, card_value="2", is_shown=True),
            Card(id=5, card_value="3", is_shown=False),
            Card(id=6, card_value="1", is_shown=True),
            ]
        
        temp_card = temporarily_hide_card_value(cards)

        expected_cards = cards
        expected_cards[1].card_value="??"
        expected_cards[2].card_value="??"
        expected_cards[4].card_value="??"

        self.assertEqual(temp_card, expected_cards)
    
    def test_start_new_game(self):
        db = {
                'test_username':{
                    'click': 0,
                    'scores': [12, 16],
                    'cards' : [
                                Card(id=1, card_value="2", is_shown=True),
                                Card(id=2, card_value="1", is_shown=False)
                                ],
                    'is_match_first_card': True,
                    'opened_cards' : []
                }
            }
        expected_cards = db['test_username']['cards']
        start_new_game(db, User(username='test_username'))

        actual_card = db['test_username']['cards']

        self.assertNotEqual(actual_card, expected_cards)
        self.assertEqual(len(actual_card), 12)
    
    def test_get_user_info(self):
        db = {
                'test_user': {
                    'username': 'test_user',
                    'full_name': 'Test Code',
                    'email': 'test@example.com',
                    'hashed_password': 'test_password',
                    'disabled': False,
                }
             }
        actual_user = get_user_info(db, 'test_user')

        self.assertEqual(actual_user.username, 'test_user')
        self.assertEqual(actual_user.full_name, 'Test Code')
        self.assertEqual(actual_user.email, 'test@example.com')
        self.assertEqual(actual_user.hashed_password, 'test_password')
        self.assertFalse(actual_user.disabled)

    def test_verify_password(self):
        hashed_password = pwd_context.hash('test_password')
        actual_verify = verify_password('test_password', hashed_password)
        self.assertTrue(actual_verify)

        actual_verify = verify_password('test_password_01', hashed_password)
        self.assertFalse(actual_verify)

        
    

if __name__ == '__main__':
   unittest.main()
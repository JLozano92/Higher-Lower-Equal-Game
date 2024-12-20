import pydealer

import numpy as np

# Instructions

# TO-DO: Implement the system for how the comparisons will be made
class GameEngine:

    hle_ranks = {
        "values": {
            "Ace": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "Jack": 11,
            "Queen": 12,
            "King": 13,
        }
    }

    hle_suits = {
        "suits": ["Spades", "Hearts", "Clubs", "Diamonds"],
    }

    def __init__(self):
        self.player_score = 0
        self.cpu_score = 0
        self.sample_deck = pydealer.Deck(ranks=self.hle_ranks, suits=self.hle_suits)

    # Returns the value of the card
    def card_value(self, card):
        return self.hle_ranks["values"][card.value]

    def terminate_game(self):
        # If player_score == 50 or cpu_score == 50 end the game
        if self.player_score == 50 or self.cpu_score == 50:
            return True

    # This is our first method that uses probability and builds upon data from the choices that were made by the player
    def naive_bayes(self):
        pass

    # Looks at the utility of every card left in the stack and offers option
    def expectimax(self, isPlayer):
        
        # If it is the players turn
        if isPlayer:
            best_move = -np.inf
            pass 
            return best_move
        
        # If it is the CPU's turn
        elif not isPlayer:
            best_move = np.inf
            pass 
            return best_move
        


newGame = GameEngine()
newGame.sample_deck.shuffle()
players_hand = newGame.sample_deck.deal(3)
cpu_hand = newGame.sample_deck.deal(3)

print("Player: ")
print(players_hand)

print("CPU: ")
print(cpu_hand)

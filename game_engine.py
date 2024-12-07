import pydealer
import pandas as pd
import numpy as np
import random # for CPU to make random guesses in the game

# Something other than higher, lower or equal exception
class InvalidClassError(Exception):
    pass

# For guesses of card values
class OutOfRangeError(Exception):
    pass

class Player:
    def __init__(self):
        # Each player will have a score and a hand of cards that are dealt in the main loop
        self.score = 0
        self.hand = pydealer.Stack()

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

        self.player = Player()
        self.cpu = Player()
        self.sample_deck = pydealer.Deck(ranks=self.hle_ranks, suits=self.hle_suits)
        self.discard_stack = pydealer.Stack()  # The stack of cards that will be accumulating cards if the game goes past using the 46 cards.

    # Returns the value of the card
    def card_value(self, card):
        return self.hle_ranks["values"][card.value]

    # Refills the stack in case deck runs out of the 46 cards
    def refill_stack(self):
        self.sample_deck.add(self.discard_stack)
        self.sample_deck.shuffle()
        self.discard_stack.clear()

    # Checks if the game should end
    def terminate_game(self):
        # If player score == 50 or cpu score == 50 end the game
        return self.player.score >= 50 or self.cpu.score >= 50

    # Deals card to player/cpu and updates score based on guess, returns how many points were won/lost
    def score_system(self, card_dealt, next_card, guess, player_type="player"):

        # Our result will be the absolute difference between the two cards; which will be added or deducted from the player's score
        result = abs(self.card_value(next_card) - self.card_value(card_dealt))
        flag = True # Default True if the player guesses correctly, False otherwise

        # Check current player
        if player_type == "player":
            player = self.player
        elif player_type == "cpu":
            player = self.cpu
        else:
            raise ValueError("Invalid player type.")

        match guess:
            case "Higher":
                if self.card_value(next_card) > self.card_value(card_dealt):
                    player.score += result
                    flag = True
                elif self.card_value(next_card) == self.card_value(card_dealt):
                    player.score -= 5
                    if player.score - 5 < 0:
                        player.score = 0
                    flag = False # If the cards are actually equal, the player loses 5 points
                    return (flag, 5)
                else:
                    player.score -= result
                    if player.score - result < 0:
                        player.score = 0
                    flag = False
            case "Lower":
                if self.card_value(next_card) < self.card_value(card_dealt):
                    player.score += result
                    flag = True
                elif self.card_value(next_card) == self.card_value(card_dealt):
                    player.score -= 5
                    flag = False
                    return (flag, 5)
                else:
                    player.score -= result
                    if player.score - result < 0:
                        player.score = 0
                    flag = False
            case "Equal":
                if self.card_value(next_card) == self.card_value(card_dealt):
                    player.score += 20
                    flag = True
                else:
                    player.score -= 20
                    if player.score - 20 < 0:
                        player.score = 0
                    flag = False
                    return (flag, 20)
            case _:
                print("Exception occurred.")
                raise InvalidClassError("Invalid class provided.")

        # Tuple has two values: flag (True/False) and result (points won/lost)
        return (flag, result)


# Class designed specifically for the CPU to make guesses in the game
class CPU(GameEngine):

    # Our CPU will not be given expectimax or naive bayes capabilities, it will be making random guesses in the game based on separate logic
    def __init__(self):
        super().__init__()

    # Used to make a guess based on cards in CPU's hand using a different strategy
    def make_guess(self, hand, deck):

        best_card = None
        max_score = -np.inf

        # Get the biggest potential score out of the three cards in the hand
        for card in hand:
            score = self.card_potential(self.card_value(card), deck.size)
            if score > max_score:
                max_score = score
                best_card = card

        # Make guesses based on the cards

        if self.card_value(best_card) <= 4:
            return (best_card, "Higher")
        elif self.card_value(best_card) >= 10:
            return (best_card, "Lower")
        elif 5 <= self.card_value(best_card) <= 9:
            return (best_card, random.choice(["Higher", "Lower", "Equal"]))  # Random guess for middle values
        else:
            if not (1 <= self.card_value(best_card) <= 13):
                raise OutOfRangeError("Card value out of range.")

    # Calculate how good a card is for the given game state
    def card_potential(self, card_value, deck_size):
        # Total number of possible card values (13 in a standard deck)
        vals = len(self.hle_ranks["values"]) # Gets all values of cards possible
        vals = len(self.hle_ranks["values"]) # Gets all values of cards possible

        # Get how many cards could be lower or higher than the curent card
        higher_than = vals - card_value #e.g. 13 - card value 10 = 3 cards higher than 10
        lower_than = card_value - 1 #e.g. 4 - 1 = 3 cards lower than 4

        score = 0

        # Extreme values that can factor into whether the CPU guesses higher or lower
        if card_value in [1,13]:
            score += 7
        elif card_value in [2,12]:
            score += 5
        elif card_value in [6,7,8]:
            score += 3
        else: # For the rest of the values
            score += 1

        score += max(higher_than, lower_than) # Add the maximum of the two values to the score
        if deck_size > 0:
            score *= (deck_size/52) # Multiply the score by the fraction of the deck left
        else: # If the deck is empty, the score will be 0
            score = 0
        score *= (deck_size/52) # Multiply the score by the fraction of the deck left

        return score



class Expectimax(GameEngine):
    """Used for doing expectimax calculations for the game (Player's assistance only)"""

    def __init__(self):
        super().__init__()
        self.expected_value = 0

    # Looks at the utility of every card left in the stack and offers which of player's card to choose AND what choice they should make.
    def expectimax(self, hand, deck):

        # Our expected value and predicted move will be at worst case scenario first.
        # This is our initial expected value while we look for better expected values in the loops below
        maxEV = -np.inf
        best_move = None

        # The fraction to compute each expected value
        probability = 1 / deck.size

        # Expectimax calculated through going down the tree of all possible moves
        for card in hand:  # First level, go through each card in the hand
            for guess in ["Higher", "Lower", "Equal"]:  # Go through each option the player has
                for current_card in deck:  # Go through every card in the deck and find the maximum expected value
                    if (guess == "Higher"):  # Circumstance for every outcome, right or wrong guesses
                        utility = (abs(self.card_value(current_card) - self.card_value(card))
                            if self.card_value(current_card) > self.card_value(card)
                            else -abs(self.card_value(current_card) - self.card_value(card)))
                        # The utility is the absolute difference between the two cards if the current card is higher than the card in hand, otherwise it is the negative of the absolute difference
                    elif guess == "Lower":
                        utility = (
                            abs(self.card_value(current_card) - self.card_value(card))
                            if self.card_value(current_card) < self.card_value(card)
                            else -abs(
                                self.card_value(current_card) - self.card_value(card)
                            )
                        )
                        # Utility is same as above, but in the case that the current card is lower than the card in hand
                    else:  # guess == "Equal"
                        utility = 20 if self.card_value(current_card) == self.card_value(card) else -20  # 20 total points will be added if the card is equal to current card in hand, the same amount is deducted otherwise

                    self.expected_value = probability * utility  # Expected value will

            # Check if new expected value is better than the current best expected value
            if self.expected_value > maxEV:
                maxEV = self.expected_value
                best_move = (card, guess)

        return maxEV, best_move


class NaiveBayes(GameEngine):
    def __init__(self):
        super().__init__()  # Go back to later
        self.training_data = pd.DataFrame(columns=["Card1", "Card2", "Card3", "Class"])
        self.class_probs = {
            "Higher": self.training_data["Class"].value_counts()["Higher"] / len(self.training_data),
            "Lower": self.training_data["Class"].value_counts()["Lower"] / len(self.training_data),
            "Equal": self.training_data["Class"].value_counts()["Equal"] / len(self.training_data),
        }  # Probabilities of each class given data of successful guesses

    def update_class_probs(self):
        if len(self.training_data) >= 1:
            self.class_probs = {
                "Higher": self.training_data["Class"].value_counts().get("Higher", 0) / len(self.training_data),
                "Lower": self.training_data["Class"].value_counts().get("Lower", 0) / len(self.training_data),
                "Equal": self.training_data["Class"].value_counts().get("Equal", 0) / len(self.training_data),
            }

    # To calculate conditional probability, we must consider P(Class|Card1, Card2, Card3) = P(Class) * P(Card1|Class) * P(Card2|Class) * P(Card3|Class)
    # Given a current hand, we will calculate the probability of each class and return an list of each probability, and the highest probability in a tuple
    def conditional_prob(self, current_hand):

        classes = list(self.class_probs.keys())  # "higher", "Lower", "Equal" as a lis ["Higher", "Lower", "Equal"]

        # Get count of each class in the Classes column of the training data i.e. 9, 5, 6 in a set of 20
        class_counts = [ self.training_data["Class"].value_counts()[class_type] for class_type in classes]

        # In the order: higher, lower, equal
        probabilities = []

        # Probability can be calculated as:
        # P(Class|Card1, Card2, Card3) = P(Class) * P(Card1|Class) * P(Card2|Class) * P(Card3|Class)

        for class_type in classes:
            temp_prob = self.class_probs[class_type]  # P(Current Class)

            for i, card in enumerate(current_hand):
                # temp_prob *= P(Cardx|Class) for each class
                card_value = self.card_value(card)  # Gets card values from current_hand

                # Conditional probability of each card and each class in the loop
                matching_rows = len(self.training_data[(self.training_data.iloc[:, i] == card_value) & (self.training_data["Class"] == class_type)])

                # Since we have probabilities that will equate to zero, we need to handle this with Laplace smoothing where alpha = 1. This is to avoid zero probabilities.

                temp_prob *= (matching_rows + 1) / (class_counts[classes.index(class_type)] + 3)

            # Append conditional probability of each class to the probabilities list
            probabilities.append(temp_prob)

        max_class = classes[probabilities.index(max(probabilities))]  # Get the class with the highest probability
        # Return all the probabilities and the class with the highest probability and its probability in a tuple
        return (probabilities, (max(probabilities), max_class))

    # Update training data with the three cards from player and class of outcome
    def update_data(self, current_hand, outcome):
        new_row = []

        for i in current_hand:
            new_row.append(self.card_value(i))

        match outcome:
            case "Higher":
                new_row.append("Higher")
                # attach class higher to training data column 4
            case "Lower":
                new_row.append("Lower")
                # attach class lower to training data column 4
            case "Equal":
                new_row.append("Equal")
                # attach class equal to training data column 4
            case _:
                print("Exception occurred.")
                raise InvalidClassError("Invalid class provided.")

        self.training_data.loc[len(self.training_data)] = new_row
        self.update_class_probs()


newGame = GameEngine()
newGame.sample_deck.shuffle()

newGame.player.hand = newGame.sample_deck.deal(3)

newGame.cpu.hand = newGame.sample_deck.deal(3)

remaining_cards = newGame.sample_deck.size

cpu_guessing = CPU()

# Test game loop; will be used in frontend, do not use this loop for final product
while newGame.terminate_game() == False:

    # Test if deck is empty:
    if newGame.sample_deck.size == 0:
        newGame.refill_stack()

    try:
        print("Player Score: ", newGame.player.score)
        print(newGame.player.hand)

        print("CPU Score: ", newGame.cpu.score)
        print(newGame.cpu.hand)

        # Refill the stack if it runs out of cards
        if remaining_cards <= 0:
            newGame.refill_stack()

        print("Remaining cards:", remaining_cards)

        card_choice = int(input("Which card would you like to bet (0-2)? "))
        if card_choice < 0 or card_choice > 2:
            raise ValueError("Card choice out of range.")

        current_guess = input("Card is higher, lower or equal? ").capitalize()
        if current_guess not in ["Higher", "Lower", "Equal"]:
            raise ValueError("Invalid guess.")

        # Get a new card
        newCard = newGame.sample_deck.deal(1)

        # Compare with next card in deck; update score
        player_result = newGame.score_system(newGame.player.hand[card_choice], newCard[0], current_guess)

        # Get specific card name to discard
        card_name = str(newGame.player.hand[card_choice])

        discard = newGame.player.hand.get(card_name)
        newGame.discard_stack.add(discard)

        # Add new card to player's hand
        newGame.player.hand.add(newCard)

        print(f"Player next card was: {newCard[0]}")

        # Decrement remaining cards
        remaining_cards -= 1

        # CPU goes through same process
        print("CPU turn")

        # Get new card for CPU
        CPU_Card = newGame.sample_deck.deal(1)

        # CPU makes a guess which returns best card and guess (higher, lower, equal)
        # OUT OF RANGE ERROR
        CPU_guess = cpu_guessing.make_guess(newGame.cpu.hand, newGame.sample_deck)

        # Get CPU's result; ERROR
        CPU_result = newGame.score_system(CPU_guess[0], CPU_Card[0], CPU_guess[1], "cpu")

        card_name = str(newGame.cpu.hand[0])

        # Discard CPU's card and put it in stack
        discard = newGame.cpu.hand.get(card_name)
        newGame.discard_stack.add(discard)

        # Add new card to CPU's hand
        newGame.cpu.hand.add(CPU_Card)

        print(f"CPU next card was: {CPU_Card[0]}")
        print(f"CPU guessed: {CPU_guess[1]}")

        # Decrement remaining cards again for CPU
        remaining_cards -= 1


        # Print if player or CPU won, or both
        if player_result[0] == True:
            print(f"Player won {player_result[1]} points.")
        else:
            print(f"Player lost {player_result[1]} points.")

        if CPU_result[0] == True:
            print(f"CPU won {CPU_result[1]} points.")
        else:
            print(f"CPU lost {CPU_result[1]} points.")

    except (ValueError, IndexError) as e:
        print(f"Error: {e}")
        continue

# Winning statement
if newGame.player.score >= 50:
    print(f"Player won with {newGame.player.score} points!")
else:
    print(f"CPU won with {newGame.cpu.score} points!")
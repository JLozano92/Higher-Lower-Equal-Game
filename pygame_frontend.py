import pygame
import os
import random
import game_engine as ge # Game Engine Functions

pygame.init()
pygame.display.set_caption("Higher-Lower-Equal Card Game")
pygame.mouse.set_visible(True)
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

# Cursor
system = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_NO)
directory = "assets/Card SVG files/"

# Load bg image and resize
casino_bg = pygame.image.load("assets/Casino_bg.jpg")
casino_bg = pygame.transform.scale(casino_bg, (1280, 720))

# Load back card and resize
back_card =pygame.image.load("assets/BACK.png")
back_card = pygame.transform.scale(back_card, (100, 150))

# Load card svg's from directory
card_images = {}
try:
    for filename in os.listdir(directory):
        if filename.endswith('.svg'):
            full_path = os.path.join(directory, filename)

            try:
                card_image = pygame.image.load(full_path)
                card_key = os.path.splitext(filename)[0]
                card_images[card_key] = card_image
            except pygame.error as e:
                print(f"Error loading {filename}: {e}")
except FileNotFoundError:
    print(f"Directory not found: {directory}")

if card_images:
    all_card_keys = list(card_images.keys())
    top_row = random.sample(all_card_keys, 3)

    remaining_cards = [card for card in all_card_keys if card not in top_row]

    bottom_row = random.sample(remaining_cards, 3)

else:
    card_keys = []

# Top
card_positions_top = [(720, 30), (840, 30), (960, 30)]
# Middle
card_positions_middle = [(620, 270), (740, 270)]
# Bottom
card_positions_bottom = [(420, 515), (540, 515), (660, 515)]

pygame.font.init()

# Scores
title_font = pygame.font.Font(None, 48)
score_font = pygame.font.Font(None, 45)

player_score = 0
cpu_score = 0

# Buttons
button = pygame.font.Font(None, 24)

button_width = 120
button_height = 50
button_color = (250, 0, 0)
text_color = (255, 255, 255)

button_texts = [
    "Instructions",
    "Higher",
    "Lower",
    "Equal",
    "Naive Bayes",
    "Expectimax"
]

# Button positions
button_positions = [
    (120, 30),   # Instructions
    (1050, 450),   # H
    (1050, 525),   # L
    (1050, 600),   # E
    (120, 500),   # N B
    (250, 500)    # Min max
]


# Main
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(casino_bg, (0, 0))

    # Card Positions [Top]
    for i, cards in enumerate(card_positions_top):
        card_image = pygame.transform.scale(card_images[top_row[i]], (100, 150))
        screen.blit(card_image, cards)

    # Card Positions [Mid]
    for i, cards in enumerate(card_positions_middle):
        if i == 0:
            placeholder_card = pygame.Surface((100, 150), pygame.SRCALPHA)
            pygame.draw.rect(placeholder_card, (0, 0, 0), placeholder_card.get_rect(), 3)
            screen.blit(placeholder_card, cards)
        elif i == 1:
            screen.blit(back_card, cards)

    # Card Positions [Bottom]
    for i, cards in enumerate(card_positions_bottom):
        card_image = pygame.transform.scale(card_images[bottom_row[i]], (100, 150))
        screen.blit(card_image, cards)

        # Player
        player_text = title_font.render("Player", True, (255, 255, 255))
        player_text_rect = player_text.get_rect(center=(860, 530))
        screen.blit(player_text, player_text_rect)

        # CPU
        cpu_text = title_font.render("CPU", True, (255, 255, 255))
        cpu_text_rect = cpu_text.get_rect(center=(620, 50))
        screen.blit(cpu_text, cpu_text_rect)

        # Player score
        player_score_text = score_font.render(f" {player_score}", True, (255, 255, 255))
        player_score_rect = player_score_text.get_rect(center=(860, 580))
        screen.blit(player_score_text, player_score_rect)

        # CPU score
        cpu_score_text = score_font.render(f" {cpu_score}", True, (255, 255, 255))
        cpu_score_rect = cpu_score_text.get_rect(center=(620, 100))
        screen.blit(cpu_score_text, cpu_score_rect)


        def draw_buttons():
            for i, (text, switch) in enumerate(zip(button_texts, button_positions)):
                button_surface = pygame.Surface((button_width, button_height))
                button_surface.fill(button_color)

                text_surface = button.render(text, True, text_color)
                text_box = text_surface.get_rect(center=(button_width // 2, button_height // 2))

                button_surface.blit(text_surface, text_box)

                screen.blit(button_surface, switch)

        draw_buttons()

    pygame.display.update()

    clock.tick(60)

pygame.quit()

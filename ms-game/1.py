import pygame

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BAR_WIDTH = 200
BAR_HEIGHT = 20
BAR_MARGIN = 20
OIL_COLOR = (255, 255, 0)  # Yellow
EXP_COLOR = (0, 255, 255)  # Cyan

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bars Example')


# Function to draw bars
def draw_bar(surface, color, x, y, width, height, value):
    pygame.draw.rect(surface, color, (x, y, width * value, height))


# Main loop
running = True
oil_level = 0.5  # Initial oil level (between 0 and 1)
exp_level = 0.3  # Initial experience level (between 0 and 1)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update oil and experience levels (for demonstration purposes)
    oil_level += 0.001
    exp_level += 0.0005
    oil_level = min(max(oil_level, 0), 1)  # Clamp between 0 and 1
    exp_level = min(max(exp_level, 0), 1)  # Clamp between 0 and 1

    # Clear the screen
    screen.fill((0, 0, 0))  # Fill with black

    # Draw oil bar
    draw_bar(screen, OIL_COLOR, BAR_MARGIN, BAR_MARGIN, BAR_WIDTH, BAR_HEIGHT, oil_level)

    # Draw experience bar
    draw_bar(screen, EXP_COLOR, BAR_MARGIN, 2 * BAR_MARGIN + BAR_HEIGHT, BAR_WIDTH, BAR_HEIGHT, exp_level)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

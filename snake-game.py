import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Set up some constants. # Change later.
EASY = {'speed': 10, 'width': 640, 'height': 480}
MEDIUM = {'speed': 15, 'width': 800, 'height': 600}
HARD = {'speed': 20, 'width': 1024, 'height': 768}
DIFFICULTY = MEDIUM  # Default difficulty

SPEED = DIFFICULTY['speed']
WIDTH, HEIGHT = DIFFICULTY['width'], DIFFICULTY['height']
FPS = 10

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the snake and food
snake = [(200, 200), (220, 200), (240, 200)]
food = (random.randrange(0, WIDTH - 20, 20), random.randrange(0, HEIGHT - 20, 20))

# Set up the direction
direction = 'RIGHT'

# Set up the clock
clock = pygame.time.Clock()

# Set up the snake color
snake_color = (0, 255, 0)  # Initial green color

# Set up the power-ups
power_ups = []
power_up_types = ['speed_boost', 'slow_down', 'extra_life', 'score_multiplier']
power_up_durations = {
    'speed_boost': 5000,  # 5 seconds
    'slow_down': 5000,  # 5 seconds
    'extra_life': 0,  # Permanent
    'score_multiplier': 5000  # 5 seconds
}
power_up_effects = {
    'speed_boost': 2,
    'slow_down': 0.5,
    'extra_life': 1,
    'score_multiplier': 2
}
current_power_ups = {}

# Set up the obstacles
obstacles = [(random.randrange(0, WIDTH - 20, 20), random.randrange(0, HEIGHT - 20, 20)) for _ in range(10)]

# Try to get the last score from file
try:
    with open("last_score.txt", "r") as file:
        last_score = int(file.read())
        print(f"Last score: {last_score}")
except (FileNotFoundError, ValueError):
    last_score = 0
    print("No last score found. Starting from scratch!")

# Try to get the best score from file
try:
    with open("best_score.txt", "r") as file:
        best_score = int(file.read())
        print(f"Best score: {best_score}")
except (FileNotFoundError, ValueError):
    best_score = 0
    print("No best score found. Starting from best score 0!")

# Game loop
paused = False
start_time = time.time()
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif not paused:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    direction = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    direction = 'DOWN'
                elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                    direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    direction = 'RIGHT'

    if paused:
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 50, HEIGHT // 2 - 18))
        pygame.display.flip()
        continue

    # Move the snake
    if direction == 'UP':
        new_head = (snake[-1][0], snake[-1][1] - 20)
    elif direction == 'DOWN':
        new_head = (snake[-1][0], snake[-1][1] + 20)
    elif direction == 'LEFT':
        new_head = (snake[-1][0] - 20, snake[-1][1])
    elif direction == 'RIGHT':
        new_head = (snake[-1][0] + 20, snake[-1][1])

    snake.append(new_head)

    # Check if the snake has eaten the food
    if snake[-1] == food:
        food = (random.randrange(0, WIDTH - 20, 20), random.randrange(0, HEIGHT - 20, 20))
        # Generate a random color for the snake
        r = random.randrange(0, 256)
        g = random.randrange(0, 256)
        b = random.randrange(0, 256)
        snake_color = (r, g, b)
    else:
        snake.pop(0)

    # Check if the snake has eaten a power-up
    for power_up in power_ups[:]:
        if snake[-1] == power_up['position']:
            power_ups.remove(power_up)
            current_power_ups[power_up['type']] = time.time() + power_up_durations[power_up['type']]

    # Apply power-up effects
    speed_multiplier = 1
    score_multiplier = 1
    extra_life = 0
    for power_up_type, end_time in list(current_power_ups.items()):
        if time.time() > end_time:
            del current_power_ups[power_up_type]
        else:
            if power_up_type == 'speed_boost':
                speed_multiplier = power_up_effects['speed_boost']
            elif power_up_type == 'slow_down':
                speed_multiplier = power_up_effects['slow_down']
            elif power_up_type == 'extra_life':
                extra_life += power_up_effects['extra_life']
            elif power_up_type == 'score_multiplier':
                score_multiplier = power_up_effects['score_multiplier']

    # Check if the snake has hit the wall, itself, or an obstacle
    if (snake[-1][0] < 0 or snake[-1][0] >= WIDTH or
            snake[-1][1] < 0 or snake[-1][1] >= HEIGHT or
            snake[-1] in snake[:-1] or
            snake[-1] in obstacles):
        if extra_life > 0:
            extra_life -= 1
            snake = [(200, 200), (220, 200), (240, 200)]
            direction = 'RIGHT'
            continue
        else:
            print(f"Game Over! - Final Score: {len(snake) - 3}")
            if len(snake) - 3 > best_score:
                best_score = len(snake) - 3
                with open("best_score.txt", "w") as file:
                    file.write(str(best_score))
            with open("last_score.txt", "w") as file:
                file.write(str(len(snake) - 3))
            pygame.quit()
            sys.exit()

    # Generate power-ups
    if random.random() < 0.01:
        power_up_type = random.choice(power_up_types)
        power_ups.append({
            'type': power_up_type,
            'position': (random.randrange(0, WIDTH - 20, 20), random.randrange(0, HEIGHT - 20, 20))
        })

    # Draw everything
    screen.fill((0, 0, 0))
    for pos in snake:
        pygame.draw.rect(screen, snake_color, pygame.Rect(pos[0], pos[1], 20, 20))
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food[0], food[1], 20, 20))
    for power_up in power_ups:
        color = (255, 255, 0) if power_up['type'] == 'speed_boost' else (0, 255, 255)
        pygame.draw.rect(screen, color, pygame.Rect(power_up['position'][0], power_up['position'][1], 20, 20))
    for obstacle in obstacles:
        pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(obstacle[0], obstacle[1], 20, 20))
    text = font.render(f"Score: {int((len(snake) - 3) * score_multiplier)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    text = font.render(f"Last Score: {last_score}", True, (255, 255, 255))
    screen.blit(text, (WIDTH - 200, 10))
    text = font.render(f"Best Score: {best_score}", True, (255, 255, 255))
    screen.blit(text, (WIDTH - 200, 40))
    # Update the display
    pygame.display.flip()

    # Cap the framerate
    clock.tick(FPS * speed_multiplier)
import math
import pygame
import random
import time
import thorpy as tp
from fuzzylogic.defuzz import bisector, cog, mom, som, lom
from fuzzyLogic import totalRule, angle, distance, obstacle, obstacle_left, obstacle_right, direction_output, exploration, space_advantage
from raycast import get_space_density


# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 100
CELL_SIZE = 6
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
GRID_COLOR = (40, 40, 40)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
HEAD_COLOR = (0, 0, 255)  # Blue

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('100x100 Snake Game')
tp.init(screen, tp.theme_human)

# Create a speed slider using ThorPy
speedSlider = tp.SliderWithText(mode="h", length=200, min_value=10, max_value=10000, initial_value=100, show_value_on_right_side=True, text="")
#speedSlider.set_font_color((255, 255, 255))  # Set text color to white

# Create a ThorPy box to contain the slider
sliderBox = tp.Box(children=[speedSlider])

# Set the position of the slider box
sliderBox.set_topleft(10, SCREEN_HEIGHT - 50)

# Make the slider box draggable
sliderBox.set_draggable(False, False)

# Clock for controlling game speed
clock = pygame.time.Clock()

# Font for displaying score
font = pygame.font.SysFont('Arial', 20)

def draw_grid():
    """Draw the grid lines on the screen."""
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

def main():
    
    
    def get_distance_to_obstacle(snake, direction, grid_size=100):
        """
        Calculate the distance to the nearest obstacle (snake body) in the snake's direction.

        Args:
            snake (list): List of (x, y) tuples representing the snake's body segments.
            direction (tuple): Current direction vector (dx, dy) of the snake.
            grid_size (int): Size of the grid (default is 100x100).

        Returns:
            int: Distance to the nearest obstacle in grid units. Returns grid_size if no obstacle is found.
        """
        head_x, head_y = snake[0]
        dx, dy = direction

        # Iterate through cells in the direction of movement
        for distance in range(1, grid_size + 1):
            # Calculate the next cell position (with grid wrapping)
            next_x = (head_x + dx * distance) % grid_size
            next_y = (head_y + dy * distance) % grid_size

            # Check if this cell is part of the snake's body (excluding the head)
            if (next_x, next_y) in snake[1:]:
                return distance

        # No obstacle found (return max possible distance)
        return grid_size

    def get_distance_to_obstacle_left(snake, direction, grid_size=100):
        """Calculate distance to the nearest obstacle to the left of the snake's head."""
        left_dir = (direction[1], -direction[0])  # Rotate direction 90° counter-clockwise
        return get_distance_to_obstacle(snake, left_dir, grid_size)

    def get_distance_to_obstacle_right(snake, direction, grid_size=100):
        """Calculate distance to the nearest obstacle to the right of the snake's head."""
        right_dir = (-direction[1], direction[0])  # Rotate direction 90° clockwise
        return get_distance_to_obstacle(snake, right_dir, grid_size)
    
    cps_counter = 0
    cps_value = 0
    last_cps_time = time.time()
    app_running = True
    
    while app_running:
        cycles = 0
        cyclesFor25Food = 0
        prevScore = 0
        # Initial snake position and body
        snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        direction = (1, 0)  # Initial direction: right
        
        # Place initial food
        food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        while food in snake:
            food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

        score = 0
        game_over = False

        while not game_over:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True

                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_UP and direction != (0, 1):
                #         direction = (0, -1)
                #     elif event.key == pygame.K_DOWN and direction != (0, -1):
                #         direction = (0, 1)
                #     elif event.key == pygame.K_LEFT and direction != (1, 0):
                #         direction = (-1, 0)
                #     elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                #         direction = (1, 0)

            # Calculate new head position
            head_x, head_y = snake[0]
            distance_to_food = ((food[0] - head_x)**2 + (food[1] - head_y)**2)**0.5
            # Calculate absolute angle to food (in radians)
            angle_to_food = math.atan2(food[1] - snake[0][1], food[0] - snake[0][0])

            # Calculate absolute angle of snake's direction (in radians)
            angle_of_direction = math.atan2(direction[1], direction[0])

            # Compute relative angle (in radians) and normalize to [-π, π]
            relative_angle = (angle_to_food - angle_of_direction + math.pi) % (2 * math.pi) - math.pi

            # Convert to degrees
            relative_angle_degrees = math.degrees(relative_angle)

            distToObstFront = get_distance_to_obstacle(snake, direction, GRID_SIZE)
            distToObstLeft = get_distance_to_obstacle_left(snake, direction, GRID_SIZE)
            distToObstRight = get_distance_to_obstacle_right(snake, direction, GRID_SIZE)
            explorationValue = 1 if random.random() < 0.1 else 0.0
            
            space_val = get_space_density(snake, direction, GRID_SIZE)
            

            CRITICAL_DIST = 8 

            if distToObstFront < CRITICAL_DIST and distToObstLeft < CRITICAL_DIST and distToObstRight < CRITICAL_DIST:
                #print(f"!!! PANIC [F:{distToObstFront} L:{distToObstLeft} R:{distToObstRight} Space:{space_val:.2f}]")

                # Define Options
                options = {
                    'front': distToObstFront,
                    'left': distToObstLeft,
                    'right': distToObstRight
                }

                # Find the "Raw" Best Direction (Pure Distance)
                best_raw_dir = max(options, key=options.get)
                max_dist = options[best_raw_dir]
                
                final_decision = best_raw_dir

                if best_raw_dir == 'front' and max_dist < 5:
                    # We are driving into a coffin. Check if side space is massive.
                    
                    # If Space is heavily Left (<-0.4) and Left isn't instantly fatal (>1)
                    if space_val < -0.4 and distToObstLeft > 1:
                        #print("   -> OVERRIDE: Straight is dead end. Bailing LEFT to Space.")
                        final_decision = 'left'
                        
                    # If Space is heavily Right (>0.4) and Right isn't instantly fatal (>1)
                    elif space_val > 0.4 and distToObstRight > 1:
                        #print("   -> OVERRIDE: Straight is dead end. Bailing RIGHT to Space.")
                        final_decision = 'right'

                # 4. Execute the Decision
                if final_decision == 'left':
                    direction = (direction[1], -direction[0])
                elif final_decision == 'right':
                    direction = (-direction[1], direction[0])
                else:
                    pass # Go Straight 
                
            # Only run your Fuzzy Logic interpreter if the Panic Override didn't fire
            else:
                directionValue = totalRule({ angle: relative_angle_degrees, distance: distance_to_food, obstacle: distToObstFront, obstacle_right: distToObstRight, obstacle_left: distToObstLeft, exploration: explorationValue, space_advantage: space_val}, cog)
                #print(f"Direction Value: {direction_output(directionValue)} == {directionValue} | Angle: {relative_angle_degrees} | Distance to Food: {distance_to_food} | Obstacle: {distToObstFront} | Obstacle Left: {distToObstLeft} | Obstacle Right: {distToObstRight} | Exploration: {explorationValue} | Space Advantage: {space_val}")
                if directionValue is None:
                    directionValue = 1.0

                if directionValue < 0.95:  # Changed from 0.5
                    # Turn left (counter-clockwise)
                    direction = (direction[1], -direction[0])

                elif directionValue > 1.05:  # Changed from 1.5
                    # Turn right (clockwise)
                    direction = (-direction[1], direction[0])

                else: # Between 0.8 and 1.2
                    # Go straight
                    pass

            new_head = ((head_x + direction[0]) % GRID_SIZE, (head_y + direction[1]) % GRID_SIZE)

            # Check for self-collision
            if new_head in snake:
                pygame.draw.rect(screen, FOOD_COLOR, (new_head[0] * CELL_SIZE, new_head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                game_over = True
                break

            # Insert new head
            snake.insert(0, new_head)

            # Check if food is eaten
            if new_head == food:
                score += 1
                # Generate new food
                food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                while food in snake:
                    food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            else:
                # Remove tail if no food eaten
                snake.pop()

            # Draw everything
            screen.fill((0, 0, 0))
            draw_grid()

            # Draw snake
            for segment in snake[1:]:  # Skip the head (first element)
                pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Draw snake head (blue)
            pygame.draw.rect(screen, HEAD_COLOR, (snake[0][0] * CELL_SIZE, snake[0][1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Draw food
            pygame.draw.rect(screen, FOOD_COLOR, (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            cps_counter += 1
            current_time = time.time()
            
            # If 1 second has passed since the last update
            '''if current_time - last_cps_time >= 1.0:
                cps_value = cps_counter
                cps_counter = 0
                last_cps_time = current_time
                # Optional: print to console to debug lag
                # print(f"Actual CPS: {cps_value}")
            '''
            # Display score
            score_text = font.render(f'Score: {score}', True, TEXT_COLOR)
            screen.blit(score_text, (10, 10))
            
            cps_text = font.render(f'Speed: {cps_value} CPS', True, (255, 255, 0)) # Yellow color
            screen.blit(cps_text, (10, 50))
            
            cycles_text = font.render(f'Cycles: {cycles}', True, TEXT_COLOR)
            screen.blit(cycles_text, (10, 30))
            
            

            # Update slider and display
            sliderBox.update(pygame.mouse.get_rel())  # Ensure slider processes user interactions
            speedSlider.draw()
            pygame.display.flip()
            cycles += 1
            if score % 25 == 0 and prevScore != score and score != 0:
                prevScore = score
                cyclesFor25Food = cycles
                print(f"Cycles to reach {score} food: {cyclesFor25Food}")
                
            # Control game speed
            clock.tick(speedSlider.get_value())  # Adjust for difficulty
            
        if not app_running:
            break
        
        
        # Display game over message
        # screen.fill((0,0,0)) # Clear screen for clarity
        msg1 = font.render(f'Game Over! Score: {score}', True, TEXT_COLOR)
        msg2 = font.render('Press R to Restart or Q to Quit', True, TEXT_COLOR)
        
        screen.blit(msg1, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20 ))
        screen.blit(msg2, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()

        # Wait for R (restart) or Q (quit)
        waiting_for_input = True
        while waiting_for_input:
            clock.tick(15) # Reduce CPU usage during wait
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                    app_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting_for_input = False # Breaks wait loop, 'app_running' stays True -> Restart
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        waiting_for_input = False
                        app_running = False # Breaks wait loop AND outer loop -> Quit

    pygame.quit()

if __name__ == '__main__':
    main()

import json
import numpy
from numpy import random
import pygad
import time
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Import game loop
from snakeGame import main as play_snake

last_generation_time = 0

def fitness_func(ga_instance, solution, solution_idx):
    total_fitness = 0
    num_trials = 1  # Run a few times to ensure the snake isn't just getting lucky
    current_gen = ga_instance.generations_completed
    random.seed(current_gen)
    for _ in range(num_trials):
        # Call game in headless mode, passing the current genes
        total_fitness += play_snake(headless=True, genes=solution) 
    return total_fitness / num_trials

def on_generation(ga_instance):
    """This function runs every time a generation completes."""
    global last_generation_time

    current_time = time.time()
    generation_time = current_time - last_generation_time
    last_generation_time = current_time

    generation = ga_instance.generations_completed
    # ga_instance.best_solution() returns (solution, fitness, index)
    best_fitness = ga_instance.best_solution()[1] 
    avg_fitness = numpy.mean(ga_instance.last_generation_fitness)
    
    print(f"Gen {generation} | Best: {best_fitness:.2f} | Avg: {avg_fitness:.2f} | Time: {generation_time:.2f}s")

# ==========================================
# DEFINE THE SEARCH BOUNDARIES (GENE SPACE)
# ==========================================
# Optimizing 8 genes total.
gene_space = [
    {'low': -180, 'high': 0}, {'low': -180, 'high': 0}, # Genes 0, 1: Angle Left 
    {'low': -180, 'high': 0}, {'low': -180, 'high': 0}, # Genes 2, 3: Angle Left Center 
    {'low': 0, 'high': 180}, {'low': 0, 'high': 180},   # Genes 4, 5: Angle Right Center
    {'low': 0, 'high': 180}, {'low': 0, 'high': 180},   # Genes 6, 7: Angle Right 
    {'low': 0, 'high': 50}, {'low': 0, 'high': 50},     # Genes 8, 9: Obstacle Near 
    {'low': 10, 'high': 100}, {'low': 10, 'high': 100},  # Genes 10, 11: Obstacle Far 
    {'low': 0, 'high': 50}, {'low': 0, 'high': 50},     # Genes 12, 13: Obstacle Left Near 
    {'low': 10, 'high': 100}, {'low': 10, 'high': 100},  # Genes 14, 15: Obstacle Left Far 
    {'low': 0, 'high': 50}, {'low': 0, 'high': 50},     # Genes 16, 17: Obstacle Right Near 
    {'low': 10, 'high': 100}, {'low': 10, 'high': 100}  # Genes 18, 19: Obstacle Right Far 

]

# ==========================================
# CONFIGURE THE GENETIC ALGORITHM
# ==========================================
ga_instance = pygad.GA(
    num_generations=20,           # How many cycles to train (start with 30-50 to test)
    num_parents_mating=12,         # How many top performers breed
    fitness_func=fitness_func,    # The grading rubric
    sol_per_pop=100,               # How many snakes play per generation
    num_genes=len(gene_space),    # Must match the length of gene_space
    gene_space=gene_space,        # The min/max boundaries defined above
    parent_selection_type="tournament", # Changed: Tournament selection generally raises the average floor better than SSS
    K_tournament=3,
    keep_parents=6,               # Keep the top 2 snakes identical for the next generation
    crossover_type="single_point",
    mutation_type="adaptive",  # Use adaptive mutation to adjust based on fitness
    mutation_probability=[0.15, 0.02],
    on_generation=on_generation,
    parallel_processing=["process", 13]
)

# ==========================================
# RUN TRAINING AND SAVE RESULTS
# ==========================================
if __name__ == '__main__':
    print("Starting Headless Genetic Algorithm Training...")
    print("This may take a few moments. Simulating generations...")
    
    last_generation_time = time.time()
    # Run the GA
    ga_instance.run()
    
    # Fetch results
    solution, solution_fitness, solution_idx = ga_instance.best_solution()

    print(f"\nTraining Complete! Best Fitness Score: {solution_fitness}")

    # Save the best solution to a JSON file
    best_genes_list = solution.tolist() # Convert numpy array to standard Python list
    with open("best_snake_genes.json", "w") as file:
        json.dump(best_genes_list, file)

    print("Saved optimal genes to 'best_snake_genes.json'.")
    print("You can now run 'python snakeGame.py' to watch your optimized snake!")
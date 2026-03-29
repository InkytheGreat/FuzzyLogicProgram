import json
import numpy
import pygad

# Import your game loop
from snakeGame import main as play_snake

def fitness_func(ga_instance, solution, solution_idx):
    total_fitness = 0
    num_trials = 3  # Run a few times to ensure the snake isn't just getting lucky
    for _ in range(num_trials):
        # Call game in headless mode, passing the current genes
        total_fitness += play_snake(headless=True, genes=solution) 
    return total_fitness / num_trials

def on_generation(ga_instance):
    """This function runs every time a generation completes."""
    generation = ga_instance.generations_completed
    # ga_instance.best_solution() returns (solution, fitness, index)
    best_fitness = ga_instance.best_solution()[1] 
    avg_fitness = numpy.mean(ga_instance.last_generation_fitness)
    
    print(f"Gen {generation} | Best: {best_fitness:.2f} | Avg: {avg_fitness:.2f}")

# ==========================================
# DEFINE THE SEARCH BOUNDARIES (GENE SPACE)
# ==========================================
# Optimizing 8 genes total.
gene_space = [
    {'low': -180, 'high': 0}, {'low': -180, 'high': 0}, # Genes 0, 1: Angle Left 
    {'low': 0, 'high': 180}, {'low': 0, 'high': 180},   # Genes 2, 3: Angle Right 
    {'low': 0, 'high': 50}, {'low': 0, 'high': 50},     # Genes 4, 5: Obstacle Near 
    {'low': 10, 'high': 100}, {'low': 10, 'high': 100}  # Genes 6, 7: Obstacle Far 
]

# ==========================================
# CONFIGURE THE GENETIC ALGORITHM
# ==========================================
ga_instance = pygad.GA(
    num_generations=30,           # How many cycles to train (start with 30-50 to test)
    num_parents_mating=5,         # How many top performers breed
    fitness_func=fitness_func,    # The grading rubric
    sol_per_pop=15,               # How many snakes play per generation
    num_genes=8,                  # Must match the length of gene_space
    gene_space=gene_space,        # The min/max boundaries defined above
    parent_selection_type="sss",  # Steady-state selection
    keep_parents=2,               # Keep the top 2 snakes identical for the next generation
    crossover_type="single_point",
    mutation_type="random",
    mutation_percent_genes=25,     # Mutate ~2 genes per offspring to keep diversity
    on_generation=on_generation
)

# ==========================================
# RUN TRAINING AND SAVE RESULTS
# ==========================================
if __name__ == '__main__':
    print("Starting Headless Genetic Algorithm Training...")
    print("This may take a few moments. Simulating generations...")
    
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
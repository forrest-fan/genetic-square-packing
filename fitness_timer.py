import visualizer
import corners
import utils
import genetic_algorithm
import time
import numpy as np

cornerSquares = corners.readCornersFromFile("corners/18_10corners.txt")
numOfCornerSquares = 10
stats = {}

for i in range(15, 101, 5):
    stats[i] = []
    for j in range(10):
        chromosome = genetic_algorithm.generateRandomChromosome(i - numOfCornerSquares)
        
        start = time.time()
        genetic_algorithm.fitness_function(cornerSquares, chromosome, False)
        timer = time.time() - start
        stats[i].append(timer)

print("Median SD Max")
for i in stats:
    print(np.median(stats[i]), np.std(stats[i]), np.max(stats[i]))
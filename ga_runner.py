import genetic_algorithm
import corners

import sys

if len(sys.argv) != 10:
    sys.exit(1)

cornerFile = sys.argv[1]
cornerSquares = corners.readCornersFromFile(cornerFile)
n = int(sys.argv[2])
populationSize = int(sys.argv[3])
matingPoolSize = int(sys.argv[4])
numGenerations = int(sys.argv[5])
mutationProbability = float(sys.argv[6])
mutationPerBitProbability = float(sys.argv[7])
crossoverProbability = float(sys.argv[8])
selectionPressure = float(sys.argv[9])
outputFilename = "garuns/{n}_{populationSize}_{matingPoolSize}_{numGenerations}_{mutationProbability}_{mutationPerBitProbability}_{crossoverProbability}_{selectionPressure}".format(
    n=n,
    populationSize=populationSize,
    matingPoolSize=matingPoolSize,
    numGenerations=numGenerations,
    mutationProbability=mutationProbability,
    mutationPerBitProbability=mutationPerBitProbability,
    crossoverProbability=crossoverProbability,
    selectionPressure=selectionPressure
)

genetic_algorithm.genetic_algorithm(cornerSquares, n, populationSize, matingPoolSize, numGenerations, mutationProbability, mutationPerBitProbability, crossoverProbability, selectionPressure, outputFilename)

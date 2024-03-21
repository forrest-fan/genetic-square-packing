import visualizer
import utils

import random
import math
import numpy as np
import time

# Chromosome encoding
NUM_BITS_NUMBER_OF_MIDDLE_SQUARES = 8
# for each square
NUM_BITS_X_COORDINATE = 15
DIVISOR_X_COORDINATE = 1000 # divide by 1000
NUM_BITS_Y_COORDINATE = 15
DIVISOR_Y_COORDINATE = 1000 # divide by 1000
NUM_BITS_ROTATION = 10
MODULO_ROTATION = 900 # mod 900
DIVISOR_ROTATION = 10 # divide by 10
NUM_BITS_SQUARE_DIRECTION = 12
MODULO_SQUARE_DIRECTION = 3600 # mod 3600
DIVISOR_SQUARE_DIRECTION = 10 # divide by 10

def genetic_algorithm(cornerSquares, n, populationSize, matingPoolSize, numGenerations, mutationProbability, mutationPerBitProbability, crossoverProbability, selectionPressure, outputFilename):
    population = [generateRandomChromosome(n) for _ in range(populationSize)]
    generation = 0

    logs = []
    generationSummary = []

    matingTime = 0

    while generation <= numGenerations:
        print("Running generation", generation + 1, "of", numGenerations)

        startTime = time.time()
        fitnesses = [fitness_function(cornerSquares, chromosome) for chromosome in population]
        fitnessTime = time.time() - startTime
        fitnesses, population = zip(*sorted(zip(fitnesses, population)))
        generationSummary.append({
            "topFitnesses": fitnesses[:5],
            "topChromosomes": population[:5],
            "generation": generation,
            "bestFitness": min(fitnesses),
            "10percentilFitness": np.percentile(fitnesses, 10),
            "25percentileFitness": np.percentile(fitnesses, 25),
            "medianFitness": np.median(fitnesses),
            "fitnessTime": fitnessTime,
            "matingTime": matingTime
        })

        if generation == numGenerations:
            # so we have analysis of last generation
            break

        startTime = time.time()
        matingPool = rouletteWheelSelection(population, fitnesses, matingPoolSize, selectionPressure)
        nextGeneration = []

        while len(nextGeneration) < populationSize:
            randIdx1 = random.randint(0, matingPoolSize - 1)
            randIdx2 = random.randint(0, matingPoolSize - 1)
            parent1 = matingPool[randIdx1]
            parent2 = matingPool[randIdx2]
            avgParentFitness = (fitnesses[randIdx1] + fitnesses[randIdx2]) / 2

            crossed = False
            if random.random() < crossoverProbability:
                crossed = True
                crossoverPoint = random.randint(0, len(parent1) - 1)
                newChromosome1, newChromosome2 = crossover(parent1, parent2, crossoverPoint, len(parent1))
            else:
                newChromosome1 = parent1
                newChromosome2 = parent2

            mutated1 = False
            mutated2 = False
            if random.random() < mutationProbability:
                mutated1 = True
                newChromosome1, mutations1 = mutationFlipbits(newChromosome1, mutationPerBitProbability)
            if random.random() < mutationProbability:
                mutated2 = True
                newChromosome2, mutations2 = mutationFlipbits(newChromosome2, mutationPerBitProbability)

            nextGeneration.append(newChromosome1)
            nextGeneration.append(newChromosome2)

            utils.saveChromosomeInJson(logs,
                newChromosome1,
                fitness_function(cornerSquares, newChromosome1),
                generation + 1,
                (parent1, parent2) if crossed else parent1,
                avgParentFitness if crossed else fitnesses[randIdx1],
                mutations1 if mutated1 else [],
                (crossoverPoint, len(parent1)) if crossed else (-1, -1))
            
            utils.saveChromosomeInJson(logs,
                newChromosome2,
                fitness_function(cornerSquares, newChromosome1),
                generation + 1,
                (parent1, parent2) if crossed else parent2,
                avgParentFitness if crossed else fitnesses[randIdx2],
                mutations2 if mutated2 else [],
                (crossoverPoint, len(parent2)) if crossed else (-1, -1))
            
        matingTime = time.time() - startTime
        
        print("Generation", generation + 1, "done")
        population = nextGeneration
        generation += 1

    utils.saveLogsToFile(logs, outputFilename + "_chromosomes.json")
    utils.saveLogsToFile(generationSummary, outputFilename + "_summary.json")

def fitness_function(cornerSquares, chromosome, visualizeSquare=False):
    # 8 bits number of squares in middle
    n = utils.binaryToInteger(chromosome[:NUM_BITS_NUMBER_OF_MIDDLE_SQUARES])

    squares = []
    chromosomeIdx = NUM_BITS_NUMBER_OF_MIDDLE_SQUARES + 1
    for _ in range(n):
        x = utils.binaryToInteger(chromosome[chromosomeIdx:chromosomeIdx + NUM_BITS_X_COORDINATE])
        x = x / DIVISOR_X_COORDINATE
        chromosomeIdx += NUM_BITS_X_COORDINATE

        y = utils.binaryToInteger(chromosome[chromosomeIdx:chromosomeIdx + NUM_BITS_Y_COORDINATE])
        y = y / DIVISOR_Y_COORDINATE
        chromosomeIdx += NUM_BITS_Y_COORDINATE

        r = utils.binaryToInteger(chromosome[chromosomeIdx:chromosomeIdx + NUM_BITS_ROTATION])
        r = (r % MODULO_ROTATION) / DIVISOR_ROTATION
        chromosomeIdx += NUM_BITS_ROTATION

        d = utils.binaryToInteger(chromosome[chromosomeIdx:chromosomeIdx + NUM_BITS_SQUARE_DIRECTION])
        d = (d % MODULO_SQUARE_DIRECTION) / DIVISOR_SQUARE_DIRECTION
        chromosomeIdx += NUM_BITS_SQUARE_DIRECTION

        squares.append(((x, y), r, d))

    finalMiddle, finalCorners = visualizer.visualize(cornerSquares, squares, visualizeSquare)

    if len(finalMiddle) == 0 and len(finalCorners) == 0:
        # Could not get valid arrangement
        return math.inf

    boundingBox = utils.getBoundingBox(finalMiddle)
    
    left, right, top, bottom = boundingBox
    for corner in finalCorners:
        for square in corner:
            for point in square[1]:
                x, y = point
                left = min(left, x)
                right = max(right, x)
                top = max(top, y)
                bottom = min(bottom, y)
    boundingBox = (left, right, top, bottom)

    longSide = max(boundingBox[1] - boundingBox[0], boundingBox[2] - boundingBox[3])
    return longSide

def generateRandomChromosome(n):
    chromsome = ""
    chromsome += utils.integerToBinary(n, 8)
    
    for _ in range(n):
        chromsome += generateRandomBinarySequence(NUM_BITS_X_COORDINATE)
        chromsome += generateRandomBinarySequence(NUM_BITS_Y_COORDINATE)
        chromsome += generateRandomBinarySequence(NUM_BITS_ROTATION)
        chromsome += generateRandomBinarySequence(NUM_BITS_SQUARE_DIRECTION)

    return chromsome

def generateRandomBinarySequence(n):
    return ''.join([str(random.randint(0, 1)) for _ in range(n)])

def crossover(chromosome1, chromosome2, begin, end):
    begin = max(begin, NUM_BITS_NUMBER_OF_MIDDLE_SQUARES + 1)
    end = min(end, len(chromosome1))
    end = max(end, begin + 1)
    newChromosome1 = chromosome1[:begin] + chromosome2[begin:end] + chromosome1[end:]
    newChromosome2 = chromosome2[:begin] + chromosome1[begin:end] + chromosome2[end:]
    return newChromosome1, newChromosome2

def mutationFlipbits(chromosome, flipProbability):
    chromosomeList = list(chromosome)
    mutations = []
    for bit in range(NUM_BITS_NUMBER_OF_MIDDLE_SQUARES + 1, len(chromosome)):
        if random.random() < flipProbability:
            chromosomeList[bit] = '1' if chromosomeList[bit] == '0' else '0'
            mutations.append(bit)

    return ''.join(chromosomeList), mutations

# Assign probabilities to chromosomes based on their fitness, return numToSelect chromosomes in a mating pool
# higher selectionPressure means higher probability of selecting fitter chromosomes
def rouletteWheelSelection(chromosomes, fitnesses, numToSelect, selectionPressure=1):
    minSideLength = min(fitnesses)
    scores = [fitnessToScore(fitness, minSideLength, selectionPressure) for fitness in fitnesses]
    totalScore = sum(scores)
    probabilities = [score / totalScore for score in scores]

    matingPool = np.random.choice(chromosomes, numToSelect, p=probabilities, replace=False)
    return matingPool

# convert a fitness (side of bounding square) to a score for selection
# we need to do this because a smaller side is better, but we want larger score
# when fitness = minSideLength, we have highest score; as fitness increases, score decreases
# selectionPressure is a parameter that determines how quickly the score decreases
def fitnessToScore(fitness, minSideLength, selectionPressure=1):
    if fitness == math.inf or fitness == 0:
        return 0
    else:
        return minSideLength/pow(fitness, selectionPressure)

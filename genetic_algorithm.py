import visualizer
import utils
import random
import numpy as np

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

    boundingBox = utils.getBoundingBox(finalMiddle)
    for corner in finalCorners:
        cornerBoundingBox = utils.getBoundingBox(corner)
        if cornerBoundingBox[0] < boundingBox[0]:
            boundingBox = cornerBoundingBox
    
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
    newChromosome1 = chromosome1[:begin] + chromosome2[begin:end] + chromosome1[end:]
    newChromosome2 = chromosome2[:begin] + chromosome1[begin:end] + chromosome2[end:]
    return newChromosome1, newChromosome2

def mutation_flipbit(chromosome, flipProbability):
    chromosomeList = list(chromosome)
    for bit in range(len(chromosome)):
        if random.random() < flipProbability:
            chromosomeList[bit] = '1' if chromosomeList[bit] == '0' else '0'

    return ''.join(chromosomeList)

# Assign probabilities to chromosomes based on their fitness, return numToSelect chromosomes in a mating pool
# higher selectionPressure means higher probability of selecting fitter chromosomes
def roulette_wheel_selection(chromosomes, fitnesses, numToSelect, selectionPressure=1):
    minSideLength = min(fitnesses)
    scores = [area_fitness_to_score(fitness, minSideLength, selectionPressure) for fitness in fitnesses]
    totalScore = sum(scores)
    probabilities = [score / totalScore for score in scores]

    matingPool = np.random.choice(chromosomes, numToSelect, p=probabilities, replace=False)
    return matingPool

# convert a fitness (area of bounding square) to a score for selection
# when fitness = minSideLength, we have highest score; as fitness increases, score decreases
# selectionPressure is a parameter that determines how quickly the score decreases
def area_fitness_to_score(fitness, minSideLength, selectionPressure=1):
    try:
        return minSideLength/pow(fitness, selectionPressure)
    except ZeroDivisionError:
        return 0
import visualizer
import utils
import random

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
    return longSide * longSide

def generateRandomChromosome(n):
    chromsome = ""
    chromsome += utils.integerToBinary(n, 8)
    
    for _ in range(n):
        chromsome += generateRandomBinarySequence(NUM_BITS_X_COORDINATE)
        chromsome += generateRandomBinarySequence(NUM_BITS_Y_COORDINATE)
        chromsome += generateRandomBinarySequence(NUM_BITS_ROTATION)
        chromsome += generateRandomBinarySequence(NUM_BITS_SQUARE_DIRECTION)

    print("Random chromosome:", chromsome)
    return chromsome

def generateRandomBinarySequence(n):
    return ''.join([str(random.randint(0, 1)) for _ in range(n)])
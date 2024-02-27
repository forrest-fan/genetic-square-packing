import utils
import os

# Corners will remain fixed during the GA process
# We will use this to set the corners, and pass it into the first solution

def writeFormulasToFile(cornerSquareInfo):
    if os.path.exists("outputs/corners.txt"):
        os.remove("outputs/corners.txt")

    with open("outputs/corners.txt", "w") as f:
        for corner in cornerSquareInfo:
            f.write(str(len(corner)) + " corners\n")
            formulas = [utils.writeDesmosFormulas(square) for square in corner]
            for formula in formulas:
                f.write("\n".join(formula) + "\n")

        f.close()

# returns a nested list of squares that are in the corners
# uses a generation function to generate the squares, can define new ones to try different corner configs
# cornerIndex 0 is top left, move clockwise
def assembleCornerSquares(cornerSquares, generationFunction):
    squares = [generationFunction(cornerSquares[i], i) for i in range(4)]
    squares = [moveCornerTo100(corner, i) for i, corner in enumerate(squares)]
    squares = getCornerSquareInfo(squares)
    
    return squares

# build squares from corner, layer by layer
# return top-left corners of the squares
def generateFromInsideOut(numSquares, cornerIndex):
    squares = []
    cornerMultiplier = [(1, -1), (-1, -1), (-1, 1), (1, 1)]
    level = 0
    while len(squares) < numSquares:
        i = 0
        while i < level and len(squares) < numSquares:
            coordinate = tuple(val1 * val2 for val1, val2 in zip(cornerMultiplier[cornerIndex], (i, level - i)))
            
            squares.append(coordinate)
            i += 1
        level += 1

    return squares

# move the corner to respective (100, 100)
def moveCornerTo100(topLeftCoordinates, cornerIndex):
    if cornerIndex == 0:
        # top left
        movedCoordinates = [(x - 100, y + 101) for x, y in topLeftCoordinates]
    elif cornerIndex == 1:
        # top right
        movedCoordinates = [(x + 99, y + 101) for x, y in topLeftCoordinates]
    elif cornerIndex == 2:
        # bottom right
        movedCoordinates = [(x + 99, y - 100) for x, y in topLeftCoordinates]
    else:
        # bottom left
        movedCoordinates = [(x - 100, y - 100) for x, y in topLeftCoordinates]
        
    return movedCoordinates

def getCornerSquareInfo(cornerSquares):
    cornerSquareInfo = []
    for corner in cornerSquares:
        thisCorner = [utils.getSquareInfo((coordinate, 0, 0)) for coordinate in corner]
        cornerSquareInfo.append(thisCorner)

    return cornerSquareInfo

# cornerSquares is a list of 4 arrays of 3-tuples (lines, corners, d); started at (100, 100) for each corner
# this method finds and keeps the squares that are facing inwards; only these squares will "touch" the middle squares
# we find the inner-facing squares by checking whether the inner-facing corner has an adjacent square that is closer to the center
def filterCornersForInnerFacingSquaresOnly(cornerSquares):
    closerToCenter = [(1, -1), (-1, -1), (-1, 1), (1, 1)]
    filteredCorners = [[], [], [], []]
    for i in range(len(cornerSquares)):
        innerFacingCornerIndex = (i + 2) % 4
        squares = cornerSquares[i]
        for sq in squares:
            _, corners, _ = sq
            innerCorner = corners[innerFacingCornerIndex]
            closerCorner = (innerCorner[0] + closerToCenter[i][0], innerCorner[1] + closerToCenter[i][1])
            closerToX = (innerCorner[0] + closerToCenter[i][0], innerCorner[1])
            closerToY = (innerCorner[0], innerCorner[1] + closerToCenter[i][1])
            foundCloser = False
            foundX = False
            foundY = False
            for sq2 in squares:
                corner2 = sq2[1][innerFacingCornerIndex]
                if corner2 == closerCorner:
                    foundCloser = True
                    break
                    
                if corner2 == closerToX:
                    foundX = True
                if corner2 == closerToY:
                    foundY = True

            if (not foundCloser) and not (foundX and foundY):
                filteredCorners[i].append(sq)

    return filteredCorners


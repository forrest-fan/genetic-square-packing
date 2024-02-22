# This module will convert an encoded binary solution into an SVG of the solution
import utils
import corners
import math
import os

# numSquares is total number of squares in this packing
# corners is an array of length 4, each entry is the # of a squares in one corner
# remaining is an array of length (numSquares - sum(corners)), each entry is a 3-tuple
    # ((x, y), r, d) where (x, y) is the coordinates of 1 corner, r is rotation factor, d is direction to move if overlap
def visualize(numSquares, corners, remaining):
    if os.path.exists("outputs/formulas.txt"):
        os.remove("outputs/formulas.txt")
    
    if os.path.exists("outputs/finalFormulas.txt"):
        os.remove("outputs/finalFormulas.txt")

    squareInfo = [utils.getSquareInfo(square) for square in remaining]
    with open ("outputs/formulas.txt", "w") as f:
        # save formulas to plug into desmos
        for square in squareInfo:
            f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
        f.close()

    squareInfoFixed = fixOverlaps(squareInfo)
    with open ("outputs/finalFormulas.txt", "w") as f:
        # save formulas to plug into desmos
        for square in squareInfoFixed:
                f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
        f.close()

    return

# squares is an array of 3-tuples (lines, corners, d)
# returns an array of 3-tuples (lines, corners, d) with no overlaps
def fixOverlaps(squares):
    for i in range(len(squares)):
        for j in range(len(squares)):
            if i == j:
                continue

            if utils.isOverlapping(squares[i], squares[j]):
                distancesToTry, extensions = getDistancesToTry(squares[i], squares)

                # try moving the square to each distance
                for distance in distancesToTry:
                    newSquare = utils.moveSquareAlongLine(squares[i], extensions, distance)

                    # is this arrangement valid?
                    valid = True
                    for k in range(len(squares)):
                        if k == i:
                            continue
                        if utils.isOverlapping(newSquare, squares[k]):
                            valid = False
                            break
                    if valid:
                        # if valid, save to index i
                        squares[i] = newSquare
                        break
                
                # break out of j loop because overlap is guaranteed to be fixed after trying all possible distances
                break
    
    return squares

# Given a square that is overlapping, return an array of distances to try to move the square to and the extension lines
def getDistancesToTry(square, allSquares):
    # If 2 squares are overlapping, move the square in the direction specified by the square's direction
    lines, corners, d = square

    # extend the corners of the square in the direction of d
    extensions = [utils.getBoundedLineThroughPoint(d, x, y) for x, y in corners]

    # save corners to try to move the square to in the form (newCorner, cornerIndex, distanceFromOldCorner)
    # note: cornerIndex i connects side i and side (i + 3) % 4
    distancesToTry = []

    cornerIndex = 0
    for ex in extensions:
        for sq in allSquares:
            if sq == square:
                continue

            # check if the extension intersects with any other square
            # this is where the old corner will be moved to
            for side in sq[0]:
                intersection = utils.getIntersection(ex, side)
                if intersection is not None:
                    dist = utils.getDistance(corners[cornerIndex], intersection)
                    distancesToTry.append(dist)

        cornerIndex += 1

    # also try extending from all other squares
    oppositeD = (d + 180) % 360
    for sq in allSquares:
        if sq == square:
            continue

        _, otherCorners, _ = sq
        for corner in otherCorners:
            otherExtension = utils.getBoundedLineThroughPoint(oppositeD, corner[0], corner[1])

            for side in lines:
                intersection = utils.getIntersection(otherExtension, side)
                if intersection is not None:
                    dist = utils.getDistance(corner, intersection)
                    distancesToTry.append(dist)

    # sort cornersToTry by distance from old corner; we want to move the square as little as possible
    distancesToTry.sort()

    return distancesToTry, extensions

def visualizeMiddleSquares(middleSquares):
    boundingBox = getBoundingBoxForMiddle(middleSquares)
    centeredSquares = moveMiddleSquaresToCenter(middleSquares, boundingBox)
    if os.path.exists("outputs/centeredSquares.txt"):
        os.remove("outputs/centeredSquares.txt")

    with open ("outputs/centeredSquares.txt", "w") as f:
            # save formulas to plug into desmos
            for square in centeredSquares:
                    f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
            f.close()

# middleSquares is an array of 3-tuples (lines, corners, d) (overlaps should be fixed already)
# cornerSquares is a list of 4 arrays of 3-tuples (lines, corners, d); started at (100, 100) for each corner
# returns an array of 3-tuples (lines, corners, d) with no overlaps
def wrapMiddleWithCorners(middleSquares, cornerSquares):
    # create 45 degree extensions from each corner
    
    pass

# middleSquares is an array of 3-tuples (lines, corners, d) (overlaps should be fixed already)
# returns the bounding box for the middle squares in the form (left, right, top, bottom)
def getBoundingBoxForMiddle(middleSquares):
    left = math.inf
    right = -math.inf
    top = -math.inf
    bottom = math.inf

    for square in middleSquares:
        _, corners, _ = square
        for corner in corners:
            x, y = corner
            left = min(left, x)
            right = max(right, x)
            top = max(top, y)
            bottom = min(bottom, y)

    return (left, right, top, bottom)

# middleSquares is an array of 3-tuples (lines, corners, d) (overlaps should be fixed already)
# boundingBox is a 4-tuple (left, right, top, bottom)
# moves all squares so that the center of the bounding box is at (0, 0), returns a list of the new squares
def moveMiddleSquaresToCenter(middleSquares, boundingBox):
    left, right, top, bottom = boundingBox
    middleX = (left + right) / 2
    middleY = (top + bottom) / 2

    moveX = 0 - middleX
    moveY = 0 - middleY

    # move all squares so that the center of the bounding box is at (0, 0)
    newSquares = [utils.moveSquare(square, moveX, moveY) for square in middleSquares]

    return newSquares

# square is a 3-tuple (lines, corners, d)
# moveX and moveY are values to move along the x and y axes
# returns a new square tuple after moving by moveX and moveY
def moveSquare(square, moveX, moveY):
    lines, corners, d = square
    newCorners = [(x + moveX, y + moveY) for x, y in corners]
    newSides = []
    for i in range(4):
        newSides.append(getBoundedFunctionForSide(newCorners[i], newCorners[(i + 1) % 4]))
    return (newSides, newCorners, d)

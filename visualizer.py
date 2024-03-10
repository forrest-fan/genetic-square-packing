# This module will convert an encoded binary solution into an SVG of the solution
import utils
from corners import filterCornersForInnerFacingSquaresOnly
import math
import os

# corners is an array of length 4, each element is an array of the squares in the corner (this will be fixed throughout the GA process)
# middle is an array of length (numSquares - sum(corners)), each entry is a 3-tuple
    # ((x, y), r, d) where (x, y) is the coordinates of 1 corner, r is rotation factor, d is direction to move if overlap
def visualize(corners, middle, writeToFile=False):
    squareInfo = [utils.getSquareInfo(square) for square in middle]
    squareInfoFixed = fixOverlaps(squareInfo)
    
    if writeToFile:
        if os.path.exists("outputs/formulas.txt"):
            os.remove("outputs/formulas.txt")
        with open ("outputs/formulas.txt", "w") as f:
            # save formulas to plug into desmos
            for square in squareInfo:
                f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
            f.close()
        
        if os.path.exists("outputs/finalFormulas.txt"):
            os.remove("outputs/finalFormulas.txt")
        with open ("outputs/finalFormulas.txt", "w") as f:
            # save formulas to plug into desmos
            for square in squareInfoFixed:
                    f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
            f.close()

    newMiddle, newCorners = wrapMiddleWithCorners(squareInfoFixed, corners, writeToFile)

    return newMiddle, newCorners

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
    boundingBox = utils.getBoundingBox(middleSquares)
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
def wrapMiddleWithCorners(middleSquares, cornerSquares, writeToFile=False):
    if sum([len(corner) for corner in cornerSquares]) == 0:
        return [], []
        
    # create 45 degree extensions from each corner
    middleSquares = moveMiddleSquaresToCenter(middleSquares, utils.getBoundingBox(middleSquares))
    innerCorners = filterCornersForInnerFacingSquaresOnly(cornerSquares)

    cornerExtensions = get45ExtensionsFromCorners(innerCorners)
    distancesToTry = getDistancesToTryForCorners(innerCorners, middleSquares, cornerExtensions)

    newCorners = tryMovingCorners(cornerSquares, middleSquares, distancesToTry)
    if newCorners is None:
        print("FAILED!")
        return [], []

    if writeToFile:
        if os.path.exists("outputs/corner_and_middle.txt"):
            os.remove("outputs/corner_and_middle.txt")

        with open("outputs/corner_and_middle.txt", "w") as f:
            for square in middleSquares:
                f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
            for corner in newCorners:
                for square in corner:
                    f.write("\n".join(utils.writeDesmosFormulas(square)) + "\n")
            f.close()

    return middleSquares, newCorners

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

# get 45-degree lines extending from all the corners in the corners
def get45ExtensionsFromCorners(innerCorners):
    angles = [315, 225, 135, 45]
    extensions = []
    for i in range(len(innerCorners)):
        pointsToExtendFrom = set()
        for squares in innerCorners[i]:
            _, corners, _ = squares
            for j in range(len(corners)):
                if j == i:
                    # skip the outer corner, it's redundant with inner
                    continue
                pointsToExtendFrom.add(corners[j])
        
        for point in pointsToExtendFrom:
            extensions.append(utils.getBoundedLineThroughPoint(angles[i], point[0], point[1]))
    
    return extensions

# get distances to try for moving the corners to the middle squares
def getDistancesToTryForCorners(innerCorners, middleSquares, cornerExtensions):
    distancesToTry = []
    maxDist = 100 * math.sqrt(2)

    # extend corners towards middle
    for extension in cornerExtensions:
        for square in middleSquares:
            for side in square[0]:
                intersection = utils.getIntersection(extension, side)
                if intersection is not None:
                    a, b, c, bound = extension
                    x = bound[0] if bound[0] != -math.inf else bound[1]
                    y = (c - a*x) / b
                    dist = utils.getDistance((x, y), intersection)
                    if dist < maxDist:
                        distancesToTry.append(dist)

    angles = [135, 45, 315, 225]
    # extend middle squares towards corners
    for square in middleSquares:
        for i in range(len(innerCorners)):
            extensions = [utils.getBoundedLineThroughPoint(angles[i], x, y) for x, y in square[1]]
            for j in range(len(extensions)):
                for cornerSquare in innerCorners[i]:
                    for side in cornerSquare[0]:
                        intersection = utils.getIntersection(extensions[j], side)
                        if intersection is not None:
                            dist = utils.getDistance(square[1][j], intersection)
                            if dist < maxDist:
                                distancesToTry.append(dist)

    return distancesToTry

def tryMovingCorners(cornerSquares, middleSquares, distancesToTry):
    distancesToTry.sort(reverse=True)
    moveMultiplier = [(1, -1), (-1, -1), (-1, 1), (1, 1)]
    for distance in distancesToTry:
        xyDist = distance / math.sqrt(2)
        newCorners = []
        for i in range(len(cornerSquares)):
            newCorners.append([utils.moveSquare(square, xyDist * moveMultiplier[i][0], xyDist * moveMultiplier[i][1]) for square in cornerSquares[i]])

        # check if the new arrangement is valid
        if not isCornerMiddleOverlap(newCorners, middleSquares) and not isCornerCornerOverlap(newCorners):
            return newCorners
    
    return None
        
def isCornerMiddleOverlap(cornerSquares, middleSquares):
    for corner in cornerSquares:
        for cornerSquare in corner:
            for square in middleSquares:
                if utils.isOverlapping(cornerSquare, square):
                    return True
                
    return False

def isCornerCornerOverlap(cornerSquares):
    topleftRight, topleftBottom = cornerSquares[0][0][1][0]
    toprightLeft, toprightBottom = cornerSquares[1][0][1][0]
    bottomrightLeft, bottomrightTop = cornerSquares[2][0][1][0]
    bottomleftRight, bottomleftTop = cornerSquares[3][0][1][0]

    for square in cornerSquares[0]:
        for corner in square[1]:
            topleftRight = max(topleftRight, corner[0])
            topleftBottom = min(topleftBottom, corner[1])
    
    for square in cornerSquares[1]:
        for corner in square[1]:
            toprightLeft = min(toprightLeft, corner[0])
            toprightBottom = min(toprightBottom, corner[1])

    for square in cornerSquares[2]:
        for corner in square[1]:
            bottomrightLeft = min(bottomrightLeft, corner[0])
            bottomrightTop = max(bottomrightTop, corner[1])
    
    for square in cornerSquares[3]:
        for corner in square[1]:
            bottomleftRight = max(bottomleftRight, corner[0])
            bottomleftTop = max(bottomleftTop, corner[1])

    return topleftRight > toprightLeft or toprightBottom < bottomrightTop or bottomrightLeft < bottomleftRight or bottomleftTop > topleftBottom

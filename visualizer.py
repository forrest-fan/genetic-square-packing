# This module will convert an encoded binary solution into an SVG of the solution

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

    squareInfo = [getSquareInfo(square) for square in remaining]
    with open ("outputs/formulas.txt", "w") as f:
        # save formulas to plug into desmos
        for square in squareInfo:
            f.write("\n".join(writeDesmosFormulas(square)) + "\n")
        f.close()

    squareInfoFixed = fixOverlaps(squareInfo)
    with open ("outputs/finalFormulas.txt", "w") as f:
        # save formulas to plug into desmos
        for square in squareInfoFixed:
                f.write("\n".join(writeDesmosFormulas(square)) + "\n")
        f.close()

    return

def writeDesmosFormulas(square):
    formulas = []
    for side in square[0]:
        formulas.append(writeDesmosFormulaForLine(side))

    return formulas

def writeDesmosFormulaForLine(line):
    a, b, c, bound = line
    low, high, xOrY = bound
    formula = "{a}x + {b}y + {c} = 0 {bound}"
    if low == -math.inf:
        boundString = "\\left\\{{{xOrY} \\leq {high}\\right\\}}".format(high=high, xOrY=xOrY)
    elif high == math.inf:
        boundString = "\\left\\{{{low} \\leq {xOrY}\\right\\}}".format(low=low, xOrY=xOrY)
    else:
        boundString = "\\left\\{{{low} \\leq {xOrY} \\leq {high}\\right\\}}".format(low=low, high=high, xOrY=xOrY)
    return formula.format(a=a, b=b, c=c, bound=boundString)


# square is a 3-tuple ((x, y), r, d)
# returns a 3-tuple (lines, corners, d)
# where lines is the 4 lines of the square in the form ax + by + c = 0 and the bounds in the form (a, b, c, bound); bound is a 3-tuple in the form (low, high, xOrY)
# corners is the 4 corners in the form [(x, y)...]
# and d is from the input
def getSquareInfo(square):
    point, r, d = square
    x, y = point
    s = math.cos(math.radians(r))
    t = math.sin(math.radians(r))

    # corners in clockwise order
    corners = [(x, y), (x + s, y - t), (x + s - t, y - t - s), (x - t, y - s)]

    # formula for sides
    sides = []
    for i in range(4):
        c1 = corners[i]
        c2 = corners[(i + 1) % 4]
        sides.append(getBoundedFunctionForSide(c1, c2))

    return (sides, corners, d)

# point1 and point2 are 2-tuples (x, y)
# returns the function ax + by + c = 0 in the form (a, b, c, bound)
def getBoundedFunctionForSide(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x2 == x1:
        # vertical line
        bound = (min(y1, y2), max(y1, y2), "y")
        return (1, 0, x1 * -1, bound)
    else:
        slope = (y2 - y1) / (x2 - x1)
        yIntercept = y1 - slope * x1
        bound = (min(x1, x2), max(x1, x2), "x")
        return (slope * -1, 1, yIntercept * -1, bound)

# checks if 2 squares are overlapping
# square is a 3-tuple (sides, corners, d)
# returns true if the squares overlap, false otherwise
def isOverlapping(square1, square2):
    sides1, corners1, _ = square1
    sides2, corners2, _ = square2

    for side1 in sides1:
        for side2 in sides2:
            intersection = getIntersection(side1, side2)
            if intersection is not None:
                isIntersectionValid = False
                # If 2 sides are intersecting, and the intersection point is not a corner of either square, then the squares are overlapping
                for corner in corners1:
                    if arePointsEqualFloatArithmeticSafe(corner, intersection):
                        isIntersectionValid = True
                    
                for corner in corners2:
                    if arePointsEqualFloatArithmeticSafe(corner, intersection):
                        isIntersectionValid = True
                    
                # TO DO WHAT IF A CORNER IS ON A SIDE, BUT IT INTERSECTS IN THE OTHER DIRECTION!?
                if not isIntersectionValid:
                    return True
            
    return False

# side is a 4-tuple (a, b, c, bound)
# returns intersction point (x, y) if the sides intersect, None otherwise
def getIntersection(side1, side2):
    a1, b1, c1, bound1 = side1
    a2, b2, c2, bound2 = side2
    
    # Solve the system of linear equations
    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        # Lines are parallel, no intersection
        # For case where lines are the same, there are infinite intersections but does not count as overlapping
        return None

    # Calculate intersection point
    x = (b1 * c2 - b2 * c1) / determinant
    y = (a2 * c1 - a1 * c2) / determinant

    # check if intersection point is within bounds
    for bound in [bound1, bound2]:
        low, high, xOrY = bound
        if xOrY == "x" and (x < low or x > high):
            return None
        elif xOrY == "y" and (y < low or y > high):
            return None

    return (x, y)

def arePointsEqualFloatArithmeticSafe(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    return math.isclose(x1, x2, abs_tol=0.00001) and math.isclose(y1, y2, abs_tol=0.00001)

# squares is an array of 3-tuples (lines, corners, d)
# returns an array of 3-tuples (lines, corners, d) with no overlaps
def fixOverlaps(squares):
    for i in range(len(squares)):
        for j in range(len(squares)):
            if i == j:
                continue

            if isOverlapping(squares[i], squares[j]):
                distancesToTry, extensions = getDistancesToTry(squares[i], squares)

                # try moving the square to each distance
                for distance in distancesToTry:
                    newSquare = moveSquareAlongLine(squares[i], extensions, distance)

                    # is this arrangement valid?
                    valid = True
                    for k in range(len(squares)):
                        if k == i:
                            continue
                        if isOverlapping(newSquare, squares[k]):
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
    extensions = [getBoundedLineThroughPoint(d, x, y) for x, y in corners]

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
                intersection = getIntersection(ex, side)
                if intersection is not None:
                    dist = getDistance(corners[cornerIndex], intersection)
                    distancesToTry.append(dist)

        cornerIndex += 1

    # also try extending from all other squares
    oppositeD = (d + 180) % 360
    for sq in allSquares:
        if sq == square:
            continue

        _, otherCorners, _ = sq
        for corner in otherCorners:
            otherExtension = getBoundedLineThroughPoint(oppositeD, corner[0], corner[1])

            for side in lines:
                intersection = getIntersection(otherExtension, side)
                if intersection is not None:
                    dist = getDistance(corner, intersection)
                    distancesToTry.append(dist)

    # sort cornersToTry by distance from old corner; we want to move the square as little as possible
    distancesToTry.sort()

    return distancesToTry, extensions

def moveSquareAlongLine(square, extensions, distance):
    lines, corners, d = square

    newCorners = []
    for i in range(4):
        # e is corresponding extension from corner c
        # move c to new corner by moving distance along e
        newCorners.append(movePointAlongLine(corners[i], extensions[i], distance))

    newSides = []
    for i in range(4):
        # connect 4 corners to get 4 sides
        newSides.append(getBoundedFunctionForSide(newCorners[i], newCorners[(i + 1) % 4]))

    return (newSides, newCorners, d)


# d is a direction represented as an angle, (x, y) is a point the line goes through
# returns the line in the form (a, b, c, bound)
def getBoundedLineThroughPoint(d, x, y):
    # vertical lines
    if d == 90:
        # line points up, so has lower bound, no upper bound
        return (1, 0, x * -1, (y, math.inf, "y"))
        
    if d == 270:
        # line points down, so has upper bound, no lower bound
        return (1, 0, x * -1, (-math.inf, y, "y"))
    
    slope = math.tan(math.radians(d))
    yIntercept = y - slope * x

    bound = (x, math.inf, "x") if d < 90 or d > 270 else (-math.inf, x, "x")

    return (slope * -1, 1, yIntercept * -1, bound)

# returns the distance between 2 points
def getDistance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# corner is a 2-tuple (x, y), line is a 4-tuple (a, b, c, bound), distance is a value
# return new point that is distance away from corner along line
def movePointAlongLine(corner, line, distance):
    x, y = corner
    a, b, c, bound = line
    low, high, xOrY = bound

    if xOrY == "y":
        # vertical line
        if low != -math.inf:
            # has lower bound, move upward
            return (x, low + distance)
        else:
            # has upper bound, move downward
            return (x, high - distance)
    else:
        # non-vertical line
        slope = -a / b
        distX = distance / math.sqrt(1 + slope ** 2)
        distY = distance * slope / math.sqrt(1 + slope ** 2)

        if low != -math.inf:
            # has lower bound, move rightward
            return (x + distX, y + distY)
        else:
            # has upper bound, move leftward
            return (x - distX, y - distY)

def visualizeMiddleSquares(middleSquares):
    boundingBox = getBoundingBoxForMiddle(middleSquares)
    centeredSquares = moveMiddleSquaresToCenter(middleSquares, boundingBox)
    if os.path.exists("outputs/centeredSquares.txt"):
        os.remove("outputs/centeredSquares.txt")

    with open ("outputs/centeredSquares.txt", "w") as f:
            # save formulas to plug into desmos
            for square in centeredSquares:
                    f.write("\n".join(writeDesmosFormulas(square)) + "\n")
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
    newSquares = [moveSquare(square, moveX, moveY) for square in middleSquares]

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

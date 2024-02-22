import math

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

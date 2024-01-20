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

    with open ("outputs/formulas.txt", "w") as f:
        # save formulas to plug into desmos
        formula = "{a}x + {b}y + {c} = 0 {bound}"
        squareInfo = [(info[0], info[1]) for info in (getSquareInfo(square) for square in remaining)]
        for square in squareInfo:
            for side in square[0]:
                a, b, c, bound = side
                low, high, xOrY = bound
                boundString = "\\left\\{{{low} \\leq {xOrY} \\leq {high}\\right\\}}".format(low=low, high=high, xOrY=xOrY)
                fx = formula.format(a=a, b=b, c=c, bound=boundString)
                f.write(fx + "\n")

        f.close()

    return

# square is a 3-tuple ((x, y), r, d)
# returns the 4 lines of the square in the form ax + by + c = 0 and the bounds in the form (a, b, c, bound); bound is a 3-tuple in the form (low, high, xOrY)
# and the 4 corners in the form (x, y)
def getSquareInfo(square):
    point, r, d = square
    x, y = point
    s = math.cos(r)
    t = math.sin(r)

    # corners in clockwise order
    corners = [(x, y), (x + s, y - t), (x + s - t, y - t - s), (x - t, y - s)]

    # unbounded formula for sides
    sides = []
    for i in range(4):
        c1 = corners[i]
        c2 = corners[(i + 1) % 4]
        sides.append(getFunctionForSide(c1, c2))

    # bounded formula for sides
    boundedSides = []
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i + 1) % 4]
        a, b, c = sides[i]
        bound = (min(x1, x2), max(x1, x2), "x") if b != 0 else (min(y1, y2), max(y1, y2), "y")
        boundedSides.append((a, b, c, bound))

    return boundedSides, corners

# point1 and point2 are 2-tuples (x, y)
# slope is a value m
# returns the function ax + by + c = 0 in the form (a, b, c)
def getFunctionForSide(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x2 == x1:
        # vertical line
        return (1, 0, x1 * -1)
    else:
        slope = (y2 - y1) / (x2 - x1)
        yIntercept = y1 - slope * x1
        return (slope * -1, 1, yIntercept * -1)

import visualizer
import corners
import utils
import genetic_algorithm

# Test base visualizer, no overlap
squares = [((4, 3), 75, 12), ((13, 2), 45, 1), ((2, -1), 30, 2), ((2, 2), 0, 0)]
visualizer.visualize([[], [], [], []], squares, writeToFile=True)

# Test overlap detection
sq1Before = ((4, 3), 0, 0)
sq2Before = ((3.5, 2.5), 0, 0)
sq3Before = ((5, 3), 0, 0)
sq1 = utils.getSquareInfo(sq1Before)
sq2 = utils.getSquareInfo(sq2Before)
sq3 = utils.getSquareInfo(sq3Before)

print(utils.isOverlapping(sq1, sq2)) # should be true
print(utils.isOverlapping(sq1, sq3)) # should be false
visualizer.visualize([[], [], [], []], [sq1Before, sq2Before, sq3Before], writeToFile=True)

# Test overlap resolution
sq1Before = ((4, 3), 30, 45)
sq2Before = ((4, 4), 55, 122)
sq3Before = ((3, 4), 80, 25)

visualizer.visualize([[], [], [], []], [sq1Before, sq2Before, sq3Before], writeToFile=True) 

# Test multiple overlaps
sq4Before = ((3.5, 4), 12, 75)
sq5Before = ((4, 3.5), 63, 236)

visualizer.visualize([[], [], [], []], [sq1Before, sq2Before, sq3Before, sq4Before, sq5Before], writeToFile=True)

# test corner generation, moved to respective (100, 100)
cornerSquares = corners.assembleCornerSquares([12, 7, 6, 5], corners.generateFromInsideOut)
filteredCornerSquares = corners.filterCornersForInnerFacingSquaresOnly(cornerSquares)
corners.writeFormulasToFile(filteredCornerSquares)

# test moving bounding box of squares to middle
fixedSquares = visualizer.fixOverlaps([utils.getSquareInfo(sq) for sq in [sq1Before, sq2Before, sq3Before, sq4Before, sq5Before]])
visualizer.visualizeMiddleSquares(fixedSquares)

visualizer.wrapMiddleWithCorners(fixedSquares, cornerSquares)

n = 10
chromosome = genetic_algorithm.generateRandomChromosome(n)
area = genetic_algorithm.fitness_function(cornerSquares, chromosome, visualizeSquare=True)
print("Area:", area)
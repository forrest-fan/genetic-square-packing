import visualizer

# Test base visualizer, no overlap
squares = [((4, 3), 75, 12), ((13, 2), 45, 1), ((2, -1), 30, 2), ((2, 2), 0, 0)]
visualizer.visualize(0, [0, 0, 0, 0], squares)

# Test overlap detection
sq1Before = ((4, 3), 0, 0)
sq2Before = ((3.5, 2.5), 0, 0)
sq3Before = ((5, 3), 0, 0)
sq1 = visualizer.getSquareInfo(sq1Before)
sq2 = visualizer.getSquareInfo(sq2Before)
sq3 = visualizer.getSquareInfo(sq3Before)

print(visualizer.isOverlapping(sq1, sq2)) # should be true
print(visualizer.isOverlapping(sq1, sq3)) # should be false
visualizer.visualize(0, [0, 0, 0, 0], [sq1Before, sq2Before, sq3Before])

# Test overlap resolution
sq1Before = ((4, 3), 30, 45)
sq2Before = ((4, 4), 55, 122)
sq3Before = ((3, 4), 80, 25)

visualizer.visualize(0, [0, 0, 0, 0], [sq1Before, sq2Before, sq3Before]) 

# Test multiple overlaps
sq4Before = ((3.5, 4), 12, 75)
sq5Before = ((4, 3.5), 63, 236)

visualizer.visualize(0, [0, 0, 0, 0], [sq1Before, sq2Before, sq3Before, sq4Before, sq5Before])

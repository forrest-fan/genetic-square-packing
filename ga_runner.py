import genetic_algorithm
import corners
import utils

import sys
import random
import time
import multiprocessing
import numpy as np

if __name__ == "__main__" and len(sys.argv) == 10:
    cornerFile = sys.argv[1]
    cornerSquares = corners.readCornersFromFile(cornerFile)
    totalN = int(sys.argv[2])
    n = totalN - sum([len(c) for c in cornerSquares])
    populationSize = int(sys.argv[3])
    matingPoolSize = int(sys.argv[4])
    numGenerations = int(sys.argv[5])
    mutationProbability = float(sys.argv[6])
    mutationPerBitProbability = float(sys.argv[7])
    crossoverProbability = float(sys.argv[8])
    selectionPressure = float(sys.argv[9])
    outputFilename = "garuns/{n}/{populationSize}_{matingPoolSize}_{numGenerations}_{mutationProbability}_{mutationPerBitProbability}_{crossoverProbability}_{selectionPressure}".format(
        n=totalN,
        populationSize=populationSize,
        matingPoolSize=matingPoolSize,
        numGenerations=numGenerations,
        mutationProbability=mutationProbability,
        mutationPerBitProbability=mutationPerBitProbability,
        crossoverProbability=crossoverProbability,
        selectionPressure=selectionPressure
    )

    population = [genetic_algorithm.generateRandomChromosome(n) for _ in range(populationSize)]
    generation = 0

    logs = []
    tempLogs = {}
    generationSummary = []

    matingTime = 0

    while generation <= numGenerations:
        print("Running generation", generation + 1, "of", numGenerations)
        startTime = time.time()

        fitnesses = [0] * populationSize
        # threads = []
        # for i in range(populationSize):
        #     th = multiprocessing.Process(target=genetic_algorithm.parallel_fitness_helper, args=(i, cornerSquares, population[i], fitnesses, logs, generation != 0))
        #     threads.append(th)
        #     th.start()
        # for th in threads:
        #     th.join()

        for i in range(populationSize):
            genetic_algorithm.parallel_fitness_helper(i, cornerSquares, population[i], fitnesses, tempLogs, generation != 0)

        fitnessTime = time.time() - startTime
        
        for k, v in tempLogs.items():
            logs.append(v)

        fitnesses, population = zip(*sorted(zip(fitnesses, population)))
        currentSummary = {
            "topFitnesses": fitnesses[:5],
            "topChromosomes": population[:5],
            "generation": generation,
            "bestFitness": min(fitnesses),
            "10percentileFitness": np.percentile(fitnesses, 10),
            "25percentileFitness": np.percentile(fitnesses, 25),
            "medianFitness": np.median(fitnesses),
            "fitnessTime": fitnessTime,
            "matingTime": matingTime
        }
        
        generationSummary.append(currentSummary)

        if generation == numGenerations:
            # so we have analysis of last generation
            break

        startTime = time.time()
        matingPool = genetic_algorithm.rouletteWheelSelection(population, fitnesses, matingPoolSize, selectionPressure)
        nextGeneration = []

        while len(nextGeneration) < populationSize:
            randIdx1 = random.randint(0, matingPoolSize - 1)
            randIdx2 = random.randint(0, matingPoolSize - 1)
            parent1 = matingPool[randIdx1]
            parent2 = matingPool[randIdx2]
            avgParentFitness = (fitnesses[randIdx1] + fitnesses[randIdx2]) / 2

            crossed = False
            if random.random() < crossoverProbability:
                crossed = True
                crossoverPoint = random.randint(0, len(parent1) - 1)
                newChromosome1, newChromosome2 = genetic_algorithm.crossover(parent1, parent2, crossoverPoint, len(parent1))
            else:
                newChromosome1 = parent1
                newChromosome2 = parent2

            mutated1 = False
            mutated2 = False
            if random.random() < mutationProbability:
                mutated1 = True
                newChromosome1, mutations1 = genetic_algorithm.mutationFlipbits(newChromosome1, mutationPerBitProbability)
            if random.random() < mutationProbability:
                mutated2 = True
                newChromosome2, mutations2 = genetic_algorithm.mutationFlipbits(newChromosome2, mutationPerBitProbability)

            nextGeneration.append(newChromosome1)
            nextGeneration.append(newChromosome2)

            utils.saveChromosomeInJson(tempLogs,
                newChromosome1,
                generation + 1,
                (parent1, parent2) if crossed else parent1,
                avgParentFitness if crossed else fitnesses[randIdx1],
                mutations1 if mutated1 else [],
                (crossoverPoint, len(parent1)) if crossed else (-1, -1))
            
            utils.saveChromosomeInJson(tempLogs,
                newChromosome2,
                generation + 1,
                (parent1, parent2) if crossed else parent2,
                avgParentFitness if crossed else fitnesses[randIdx2],
                mutations2 if mutated2 else [],
                (crossoverPoint, len(parent2)) if crossed else (-1, -1))
            
        matingTime = time.time() - startTime
        
        print("Generation", generation + 1, "done")
        population = nextGeneration
        generation += 1

    utils.saveLogsToFile(logs, outputFilename + "_chromosomes.json")
    utils.saveLogsToFile(generationSummary, outputFilename + "_summary.json")
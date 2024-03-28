import json
import os
import sys

directory = sys.argv[1]

osDirectory = os.fsencode(directory)

allData = {}

for file in os.listdir(osDirectory):
    filename = os.fsdecode(file)
    if filename.endswith(".json"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            stats = []

            for gen in data:
                stats.append({
                    "generation": gen["generation"],
                    "bestFitness": gen["bestFitness"],
                    "p10": gen["10percentileFitness"],
                    "p25": gen["25percentileFitness"],
                    "p50": gen["medianFitness"],
                })
            
            allData[filename] = stats
            f.close()

# convert to csv
if os.path.exists("output.csv"):
    os.remove("output.csv")
    
with open ("output.csv", 'w') as f:
    for filename in allData:
        f.write(filename + "\n")
        f.write("Generation,Best Fitness,10th Percentile Fitness,25th Percentile Fitness,50th Percentile Fitness\n")
        for gen in allData[filename]:
            f.write("{},{},{},{},{}\n".format(gen["generation"], gen["bestFitness"], gen["p10"], gen["p25"], gen["p50"]))
        f.write("\n")
    f.close()
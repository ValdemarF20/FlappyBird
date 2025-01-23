import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import sem, t


def print_stats():
    for file in os.listdir("results"):
        with open(f"results/{file}", "r") as f:
            data = f.read().split("\n")
            data = [line for line in data if line != ""]

            birds_survived = [int(line.split(":")[1].split(" ")[1]) for line in data]

            # Split list into parts of 5
            birds_survived_split = [birds_survived[i:i + 5] for i in range(0, len(birds_survived), 5)]
            # Get mean of each part
            birds_survived_means = [np.mean(split) for split in birds_survived_split]

            # Calculate confidence intervals
            confidence_intervals = []
            for split in birds_survived_split:
                n = len(split)
                mean = np.mean(split)
                std_err = sem(split)
                h = std_err * t.ppf((1 + 0.95) / 2, n - 1)
                confidence_intervals.append((mean - h, mean + h))

            # Plot mean values
            plt.plot(birds_survived_means, label='Mean birds survived')

            # Plot confidence intervals
            lower_bounds = [ci[0] for ci in confidence_intervals]
            upper_bounds = [ci[1] for ci in confidence_intervals]
            plt.fill_between(range(len(birds_survived_means)), lower_bounds, upper_bounds, color='b', alpha=0.2, label='95% CI')

            plt.xlabel("Generation [5s]")
            plt.ylabel("Mean birds survived")
            plt.title("Mean birds survived per generation")
            plt.legend()
            plt.show()

if __name__ == "__main__":
    print_stats()

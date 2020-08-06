import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from configuration import CONFIGURATION

data = {
    "Cr-Cr": {
        "energy": [],
        "distance": [],
    },
    "Cr-Fe": {
        "energy": [],
        "distance": [],
    },
    "Fe-Cr": {
        "energy": [],
        "distance": [],
    },
    "Fe-Fe": {
        "energy": [],
        "distance": [],
    },
}

if __name__ == "__main__":
    dirs = os.listdir("./out")
    dirs = [d for d in dirs if os.path.isdir(os.path.join("./out", d))]
    for d in dirs:
        specie_i, specie_j, number = d.split("-")
        key = "{}-{}".format(specie_i, specie_j)
        data_path = os.path.join("./out", d, "log.lammps")
        with open(data_path, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
        parts = lines[-1].split()
        parts = [p.strip() for p in parts]
        distance = []
        energy = []
        for i, p in enumerate(parts[-2*CONFIGURATION["n_images"]:]):
            if i % 2 == 0:
                distance.append(float(p))
            else:
                energy.append(float(p))
        energy = [e - energy[0] for e in energy]
        data[key]["distance"].append(distance)
        data[key]["energy"].append(energy)
    for key in data:
        fig, ax = plt.subplots()
        peaks = [max(e) for e in data[key]["energy"]]
        density = stats.gaussian_kde(peaks)
        xs = np.linspace(min(peaks), max(peaks), 100)
        ax.plot(xs, density(xs))
        ax.hist(peaks, density=True, bins=50)
        ax.set_title(key)
        ax.set_xlabel("Barrier Height (eV)")
        ax.set_ylabel("Counts")
        filename = "{}_distribution.png".format(key)
        plt.savefig(filename)

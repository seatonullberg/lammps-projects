import os

import matplotlib.pyplot as plt
import numpy as np

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
        for distance, energy in zip(data[key]["distance"], data[key]["energy"]):
            #spline = CubicSpline(distance, energy)
            #xs = np.arange(0, 1, 0.01)
            #ax.plot(xs, spline(xs), color="blue", alpha=0.5)
            ax.plot(distance, energy, color="blue", alpha=0.2)
        ax.set_title(key)
        ax.set_ylim((-0.5, 1.6))
        ax.set_ylabel("Barrier Height (eV)")
        ax.set_xlabel("Normalized Path Length")
        filename = "{}_barrier_height.png".format(key)
        plt.savefig(filename)

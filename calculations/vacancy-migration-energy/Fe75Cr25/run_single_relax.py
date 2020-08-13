import copy
import os

# supress all warnings
# pymatgen has a LOT of them
import warnings
warnings.filterwarnings("ignore")

import numpy as np

from pymatgen.io.lammps.data import LammpsData
from pymatgen.io.lammps.inputs import write_lammps_inputs

from configuration import CONFIGURATION

# define the LAMMPS input script template for the relaxation procedure
relax_template = """clear
units      metal
atom_style atomic
boundary   p p p
read_data  $structure_path
pair_style $pair_style
pair_coeff * * $potential_path $atom_types
fix        1 all nve
minimize   1.0e-4 1.0e-6 10000 100000
fix        2 all box/relax iso 0.0 vmax 1.0e-3
minimize   1.0e-6 1.0e-8 10000 100000
fix        3 all box/relax aniso 0.0 vmax 1.0e-3
minimize   1.0e-8 1.0e-10 10000 100000
write_data $output_path
run        1000
"""

# define the LAMMPS input script template for the NEB procedure
neb_template = """clear
units          metal
atom_style     atomic
atom_modify    map array
atom_modify    sort 0 0.0
boundary       p p p
read_data      $structure_path
pair_style     $pair_style
pair_coeff     * * $potential_path $atom_types
reset_timestep 0
fix            1 all neb 1.0
thermo         100
timestep       0.01
min_style      quickmin
neb            0.0 0.01 10000 10000 100 final $neb_coords_path
"""


if __name__ == "__main__":
    # generate and enter an output directory
    os.mkdir("./out")
    os.chdir("./out")

    # relax the bulk structure
    settings = {
        "structure_path": CONFIGURATION["structure_path"],
        "pair_style": CONFIGURATION["pair_style"],
        "potential_path": CONFIGURATION["potential_path"],
        "atom_types": CONFIGURATION["atom_types"],
        "output_path": "bulk.relax.lmp"
    }
    write_lammps_inputs(".", relax_template, settings=settings)
    cmd = "$LAMMPS_SERIAL_BIN -in in.lammps >/dev/null"
    print("Running structure relaxation...")
    os.system(cmd)
    print("Completed structure relaxation.")

    # load the relaxed structure file
    lammps_data = LammpsData.from_file("bulk.relax.lmp", atom_style="atomic")
    structure = lammps_data.structure
    
    # iterate over the lattice sites
    sim_counts = {}
    for i, site_i in enumerate(structure.sites):
        for j, site_j in enumerate(structure.sites):
            # skip identical sites
            if i == j:
                continue
            
            # skip sites which are not nearest neighbors
            if site_i.distance(site_j) > CONFIGURATION["nearest_neighbor_radius"] + CONFIGURATION["tolerance"]:
                continue

            # determine the species of each site
            species_i = site_i.species_string
            species_j = site_j.species_string

            # check if sims for this pair of species are maxed out
            key = "{}-{}".format(species_i, species_j)
            if key in sim_counts:
                sim_counts[key] += 1
            else:
                sim_counts[key] = 0
            if sim_counts[key] >= CONFIGURATION["max_simulations_per_pair"]:
                continue

            # introduce a vacancy
            vacancy_structure = copy.deepcopy(structure)
            vacancy_structure.remove_sites([i])

            # create and enter a new simulation directory
            dirname = "{}-{}-{}".format(species_i, species_j, sim_counts[key])
            os.mkdir(dirname)
            print("Entering {}...".format(dirname))
            os.chdir(dirname)

            # write the vacancy structure to file
            vacancy_data = LammpsData.from_structure(vacancy_structure, atom_style="atomic")
            with open("vacancy.lmp", "w") as f:
                f.write(vacancy_data.get_string())

            # find the new index of site j
            for index, site in enumerate(vacancy_data.structure.sites):
                if site.distance(site_j) < CONFIGURATION["tolerance"]:
                    break

            # generate the NEB coords file
            with open("neb.coords", "w") as f:
                f.write("1\n{} {} {} {}".format(index + 1, site_i.x, site_i.y, site_i.z))

            # do the NEB calculation
            settings = {
                "structure_path": "vacancy.lmp",
                "pair_style": CONFIGURATION["pair_style"],
                "potential_path": CONFIGURATION["potential_path"],
                "atom_types": CONFIGURATION["atom_types"],
                "neb_coords_path": "neb.coords",
            }
            write_lammps_inputs(".", neb_template, settings=settings)
            cmd = "mpirun -np {np} --oversubscribe $LAMMPS_MPI_BIN -partition {partition} -in {input_script_path} >/dev/null"
            cmd = cmd.format(
                np=CONFIGURATION["n_images"],
                partition="{}x1".format(CONFIGURATION["n_images"]),
                input_script_path="in.lammps"
            )
            print("\tRunning NEB calculation...")
            os.system(cmd)
            print("\tCompleted NEB calculation.")

            # return to parent directory
            os.chdir("..")

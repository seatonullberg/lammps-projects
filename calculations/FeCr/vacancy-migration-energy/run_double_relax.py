import copy
import os
import shutil

# supress all warnings
# pymatgen has a LOT of them
import warnings
warnings.filterwarnings("ignore")

import numpy as np

from pymatgen.io.lammps.data import LammpsData
from pymatgen.io.lammps.inputs import write_lammps_inputs

from .configuration import CONFIGURATION

# define the LAMMPS input script template for the primary relaxation procedure
primary_relax_template = """clear
units       metal
atom_style  atomic
atom_modify map array
atom_modify sort 0 0.0
boundary    p p p
read_data   $structure_path
pair_style  $pair_style
pair_coeff  * * $potential_path $atom_types
fix         1 all nve
minimize    1.0e-4 1.0e-6 10000 100000
fix         2 all box/relax iso 0.0 vmax 1.0e-3
minimize    1.0e-6 1.0e-8 10000 100000
fix         3 all box/relax aniso 0.0 vmax 1.0e-3
minimize    1.0e-8 1.0e-10 10000 100000
write_data  $output_path
run         1000
"""

# define the LAMMPS input script template for the secondary relaxation procedure
secondary_relax_template = """clear
units       metal
atom_style  atomic
atom_modify map array
atom_modify sort 0 0.0
boundary    p p p
read_data   $structure_path
pair_style  $pair_style
pair_coeff  * * $potential_path $atom_types
fix         1 all nve
minimize    1.0e-4 1.0e-6 10000 100000
minimize    1.0e-6 1.0e-8 10000 100000
minimize    1.0e-8 1.0e-10 10000 100000
write_data  $output_path
run         1000
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
    write_lammps_inputs(".", primary_relax_template, settings=settings)
    cmd = "$LAMMPS_SERIAL_BIN -in in.lammps >/dev/null"
    print("Running primary structure relaxation...")
    os.system(cmd)
    print("Completed primary structure relaxation.")

    # load the relaxed structure file
    bulk_relax_data = LammpsData.from_file("bulk.relax.lmp", atom_style="atomic")

    # initialize simulation counter
    all_species = CONFIGURATION["atom_types"].split()
    sim_counts = {"{}-{}".format(s_i, s_j): 0 for s_i in all_species for s_j in all_species}

    # iterate over the bulk relaxed lattice sites
    for i, site_i in enumerate(bulk_relax_data.structure.sites):

        # check if simulations are maxed out
        is_complete = all([v == CONFIGURATION["max_simulations_per_pair"] for v in sim_counts.values()])
        if is_complete:
            break

        # remove old temporary directory
        if os.path.exists("./tmp"):
            shutil.rmtree("./tmp")

        # introduce a vacancy prior to secondary relaxation
        vacancy_structure = copy.deepcopy(bulk_relax_data.structure)
        vacancy_structure.remove_sites([i])

        # create and enter a temporary directory for the secondary relaxation
        os.mkdir("./tmp")
        os.chdir("./tmp")

        # write the vacancy structure to file
        vacancy_data = LammpsData.from_structure(vacancy_structure, atom_style="atomic")
        with open("vacancy.lmp", "w") as f:
            f.write(vacancy_data.get_string())

        # relax the vacancy structure
        settings = {
            "structure_path": "vacancy.lmp",
            "pair_style": CONFIGURATION["pair_style"],
            "potential_path": CONFIGURATION["potential_path"],
            "atom_types": CONFIGURATION["atom_types"],
            "output_path": "vacancy.relax.lmp",
        }
        write_lammps_inputs(".", secondary_relax_template, settings=settings)
        cmd = "$LAMMPS_SERIAL_BIN -in in.lammps >/dev/null"
        print("Running secondary structure relaxation...")
        os.system(cmd)
        print("Completed secondary structure relaxation.")

        # load the relaxed vacancy structure from file
        vacancy_relax_data = LammpsData.from_file("vacancy.relax.lmp", atom_style="atomic")

        # exit the tmp directory
        os.chdir("..")

        # iterate over the vacancy relaxed lattice sites
        for j, site_j in enumerate(vacancy_relax_data.structure.sites):

            # skip sites which are not nearest neighbors
            if site_i.distance(site_j) > CONFIGURATION["nearest_neighbor_radius"] + CONFIGURATION["tolerance"]:
                continue

            # determine the species of each site
            species_i = site_i.species_string
            species_j = site_j.species_string

            # check if sims for this pair of species are maxed out
            key = "{}-{}".format(species_i, species_j)
            if sim_counts[key] >= CONFIGURATION["max_simulations_per_pair"]:
                continue
            
            # create and enter a new simulation directory
            dirname = "{}-{}-{}".format(species_i, species_j, sim_counts[key])
            os.mkdir(dirname)
            print("Entering {}...".format(dirname))
            os.chdir(dirname)

            # generate the NEB coords file
            with open("neb.coords", "w") as f:
                f.write("1\n{} {} {} {}".format(j + 1, site_i.x, site_i.y, site_i.z))

            # do the NEB calculation
            settings = {
                "structure_path": "../tmp/vacancy.relax.lmp",
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
            sim_counts[key] += 1
            print("\tCompleted NEB calculation.")

            # return to parent directory
            os.chdir("..")

    shutil.rmtree("./tmp")

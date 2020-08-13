import os

import numpy as np

POTENTIALS_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    "potentials"
)
STRUCTURES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    "structures"
)

######################
#  GENERAL SETTINGS  #
######################
CONFIGURATION = {}
CONFIGURATION["max_simulations_per_pair"] = 500
CONFIGURATION["tolerance"] = 0.1
CONFIGURATION["atom_types"] = "Cr Fe"
CONFIGURATION["n_images"] = 17

###########################
#  Fe75Cr25 BCC SETTINGS  #
###########################
# CONFIGURATION["lattice_parameter"] = 2.86
# CONFIGURATION["nearest_neighbor_radius"] = (np.sqrt(3) * CONFIGURATION["lattice_parameter"]) / 2
# CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "FeCr_BCC_Stukowski_2009.cdeam")
# CONFIGURATION["pair_style"] = "eam/cd"
# CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Fe75Cr25_BCC_bulk_5x5x5.lmp")

###########################
#  Fe75Cr25 FCC SETTINGS  #
###########################
CONFIGURATION["lattice_parameter"] = 3.51
CONFIGURATION["nearest_neighbor_radius"] = CONFIGURATION["lattice_parameter"] / np.sqrt(2)
CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "FeCrNi_FCC_Zhou_2018.eam.alloy")
CONFIGURATION["pair_style"] = "eam/alloy"
CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Fe75Cr25_FCC_bulk_5x5x5.lmp")

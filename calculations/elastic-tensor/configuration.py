import os

import numpy as np

POTENTIALS_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "potentials"
)
STRUCTURES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "structures"
)

######################
#  GENERAL SETTINGS  #
######################
CONFIGURATION = {}

#####################
#  Fe BCC SETTINGS  #
#####################
CONFIGURATION["atom_types"] = "Cr Fe"
CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "FeCr_BCC_Stukowski_2009.cdeam")
CONFIGURATION["pair_style"] = "eam/cd"
CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Fe75Cr25_BCC_bulk_5x5x5.lmp")

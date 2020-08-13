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
#  Cr BCC SETTINGS  #
#####################
# CONFIGURATION["atom_types"] = "Cr"
# CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "FeCr_BCC_Stukowski_2009.cdeam")
# CONFIGURATION["pair_style"] = "eam/cd"
# CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Cr_BCC_bulk_1x1x1.lmp")

#####################
#  Fe BCC SETTINGS  #
#####################
# CONFIGURATION["atom_types"] = "Fe"
# CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "Fe_BCC_Olsson_2009.eam.alloy")
# CONFIGURATION["pair_style"] = "eam/alloy"
# CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Fe_BCC_bulk_1x1x1.lmp")

###########################
#  Fe75Cr25 BCC SETTINGS  #
###########################
# CONFIGURATION["atom_types"] = "Cr Fe"
# CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "FeCr_BCC_Stukowski_2009.cdeam")
# CONFIGURATION["pair_style"] = "eam/cd"
# CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Fe75Cr25_BCC_bulk_5x5x5.lmp")

###########################
#  Fe75Cr25 FCC SETTINGS  #
###########################
# CONFIGURATION["atom_types"] = "Cr Fe"
# CONFIGURATION["potential_path"] = os.path.join(POTENTIALS_DIRECTORY, "FeCrNi_FCC_Zhou_2018.eam.alloy")
# CONFIGURATION["pair_style"] = "eam/alloy"
# CONFIGURATION["structure_path"] = os.path.join(STRUCTURES_DIRECTORY, "Fe75Cr25_FCC_bulk_5x5x5.lmp")
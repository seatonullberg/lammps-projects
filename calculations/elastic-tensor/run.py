import os

# supress all warnings
# pymatgen has a LOT of them
import warnings
warnings.filterwarnings("ignore")

import numpy as np

from pymatgen.io.lammps.data import LammpsData
from pymatgen.io.lammps.inputs import write_lammps_inputs

from configuration import CONFIGURATION

# define the LAMMPS input script template for the initialization
init_template = """
variable up         equal 1.0e-6
variable atomjiggle equal 1.0e-5

units		           metal
variable cfac   equal  1.0e-4
variable cunits string GPa

variable etol    equal 0.0 
variable ftol    equal 1.0e-10
variable maxiter equal 100
variable maxeval equal 1000
variable dmax    equal 1.0e-2

boundary  p p p
read_data $structure_path
"""

# define the LAMMPS input script template for the potential description
potential_template = """
pair_style $pair_style
pair_coeff * * $potential_path $atom_types

neighbor     1.0 nsq
neigh_modify once no every 1 delay 0 check yes

min_style  cg
min_modify dmax 1.0e-2 line quadratic

thermo		  1
thermo_style  custom step temp pe press pxx pyy pzz pxy pxz pyz lx ly lz vol
thermo_modify norm no
"""

# define the LAMMPS input script template for the displacement
displace_template = """
if "${dir} == 1" then &
   "variable len0 equal ${lx0}" 
if "${dir} == 2" then &
   "variable len0 equal ${ly0}" 
if "${dir} == 3" then &
   "variable len0 equal ${lz0}" 
if "${dir} == 4" then &
   "variable len0 equal ${lz0}" 
if "${dir} == 5" then &
   "variable len0 equal ${lz0}" 
if "${dir} == 6" then &
   "variable len0 equal ${ly0}" 

clear
box tilt large
read_restart restart.equil
include potential.mod

variable delta equal -${up}*${len0}
variable deltaxy equal -${up}*xy
variable deltaxz equal -${up}*xz
variable deltayz equal -${up}*yz
if "${dir} == 1" then &
   "change_box all x delta 0 ${delta} xy delta ${deltaxy} xz delta ${deltaxz} remap units box"
if "${dir} == 2" then &
   "change_box all y delta 0 ${delta} yz delta ${deltayz} remap units box"
if "${dir} == 3" then &
   "change_box all z delta 0 ${delta} remap units box"
if "${dir} == 4" then &
   "change_box all yz delta ${delta} remap units box"
if "${dir} == 5" then &
   "change_box all xz delta ${delta} remap units box"
if "${dir} == 6" then &
   "change_box all xy delta ${delta} remap units box"

minimize ${etol} ${ftol} ${maxiter} ${maxeval}

variable tmp equal pxx
variable pxx1 equal ${tmp}
variable tmp equal pyy
variable pyy1 equal ${tmp}
variable tmp equal pzz
variable pzz1 equal ${tmp}
variable tmp equal pxy
variable pxy1 equal ${tmp}
variable tmp equal pxz
variable pxz1 equal ${tmp}
variable tmp equal pyz
variable pyz1 equal ${tmp}

variable C1neg equal ${d1}
variable C2neg equal ${d2}
variable C3neg equal ${d3}
variable C4neg equal ${d4}
variable C5neg equal ${d5}
variable C6neg equal ${d6}

clear
box tilt large
read_restart restart.equil
include potential.mod

variable delta equal ${up}*${len0}
variable deltaxy equal ${up}*xy
variable deltaxz equal ${up}*xz
variable deltayz equal ${up}*yz

if "${dir} == 1" then &
   "change_box all x delta 0 ${delta} xy delta ${deltaxy} xz delta ${deltaxz} remap units box"
if "${dir} == 2" then &
   "change_box all y delta 0 ${delta} yz delta ${deltayz} remap units box"
if "${dir} == 3" then &
   "change_box all z delta 0 ${delta} remap units box"
if "${dir} == 4" then &
   "change_box all yz delta ${delta} remap units box"
if "${dir} == 5" then &
   "change_box all xz delta ${delta} remap units box"
if "${dir} == 6" then &
   "change_box all xy delta ${delta} remap units box"

minimize ${etol} ${ftol} ${maxiter} ${maxeval}

variable tmp equal pe
variable e1 equal ${tmp}
variable tmp equal press
variable p1 equal ${tmp}
variable tmp equal pxx
variable pxx1 equal ${tmp}
variable tmp equal pyy
variable pyy1 equal ${tmp}
variable tmp equal pzz
variable pzz1 equal ${tmp}
variable tmp equal pxy
variable pxy1 equal ${tmp}
variable tmp equal pxz
variable pxz1 equal ${tmp}
variable tmp equal pyz
variable pyz1 equal ${tmp}

variable C1pos equal ${d1}
variable C2pos equal ${d2}
variable C3pos equal ${d3}
variable C4pos equal ${d4}
variable C5pos equal ${d5}
variable C6pos equal ${d6}

variable C1${dir} equal 0.5*(${C1neg}+${C1pos})
variable C2${dir} equal 0.5*(${C2neg}+${C2pos})
variable C3${dir} equal 0.5*(${C3neg}+${C3pos})
variable C4${dir} equal 0.5*(${C4neg}+${C4pos})
variable C5${dir} equal 0.5*(${C5neg}+${C5pos})
variable C6${dir} equal 0.5*(${C6neg}+${C6pos})

variable dir delete
"""

input_script = """
include init.mod
include potential.mod

fix 3 all box/relax  aniso 0.0
minimize ${etol} ${ftol} ${maxiter} ${maxeval}

variable tmp equal pxx
variable pxx0 equal ${tmp}
variable tmp equal pyy
variable pyy0 equal ${tmp}
variable tmp equal pzz
variable pzz0 equal ${tmp}
variable tmp equal pyz
variable pyz0 equal ${tmp}
variable tmp equal pxz
variable pxz0 equal ${tmp}
variable tmp equal pxy
variable pxy0 equal ${tmp}

variable tmp equal lx
variable lx0 equal ${tmp}
variable tmp equal ly
variable ly0 equal ${tmp}
variable tmp equal lz
variable lz0 equal ${tmp}

variable d1 equal -(v_pxx1-${pxx0})/(v_delta/v_len0)*${cfac}
variable d2 equal -(v_pyy1-${pyy0})/(v_delta/v_len0)*${cfac}
variable d3 equal -(v_pzz1-${pzz0})/(v_delta/v_len0)*${cfac}
variable d4 equal -(v_pyz1-${pyz0})/(v_delta/v_len0)*${cfac}
variable d5 equal -(v_pxz1-${pxz0})/(v_delta/v_len0)*${cfac}
variable d6 equal -(v_pxy1-${pxy0})/(v_delta/v_len0)*${cfac}

displace_atoms all random ${atomjiggle} ${atomjiggle} ${atomjiggle} 87287 units box

write_restart restart.equil

variable dir equal 1
include displace.mod

variable dir equal 2
include displace.mod

variable dir equal 3
include displace.mod

variable dir equal 4
include displace.mod

variable dir equal 5
include displace.mod

variable dir equal 6
include displace.mod

variable C11all equal ${C11}
variable C22all equal ${C22}
variable C33all equal ${C33}

variable C12all equal 0.5*(${C12}+${C21})
variable C13all equal 0.5*(${C13}+${C31})
variable C23all equal 0.5*(${C23}+${C32})

variable C44all equal ${C44}
variable C55all equal ${C55}
variable C66all equal ${C66}

variable C14all equal 0.5*(${C14}+${C41})
variable C15all equal 0.5*(${C15}+${C51})
variable C16all equal 0.5*(${C16}+${C61})

variable C24all equal 0.5*(${C24}+${C42})
variable C25all equal 0.5*(${C25}+${C52})
variable C26all equal 0.5*(${C26}+${C62})

variable C34all equal 0.5*(${C34}+${C43})
variable C35all equal 0.5*(${C35}+${C53})
variable C36all equal 0.5*(${C36}+${C63})

variable C45all equal 0.5*(${C45}+${C54})
variable C46all equal 0.5*(${C46}+${C64})
variable C56all equal 0.5*(${C56}+${C65})

variable C11cubic equal (${C11all}+${C22all}+${C33all})/3.0
variable C12cubic equal (${C12all}+${C13all}+${C23all})/3.0
variable C44cubic equal (${C44all}+${C55all}+${C66all})/3.0

variable bulkmodulus equal (${C11cubic}+2*${C12cubic})/3.0
variable shearmodulus1 equal ${C44cubic}
variable shearmodulus2 equal (${C11cubic}-${C12cubic})/2.0
variable poissonratio equal 1.0/(1.0+${C11cubic}/${C12cubic})

print "========================================="
print "Components of the Elastic Constant Tensor"
print "========================================="

print "Elastic Constant C11all = ${C11all} ${cunits}"
print "Elastic Constant C22all = ${C22all} ${cunits}"
print "Elastic Constant C33all = ${C33all} ${cunits}"

print "Elastic Constant C12all = ${C12all} ${cunits}"
print "Elastic Constant C13all = ${C13all} ${cunits}"
print "Elastic Constant C23all = ${C23all} ${cunits}"

print "Elastic Constant C44all = ${C44all} ${cunits}"
print "Elastic Constant C55all = ${C55all} ${cunits}"
print "Elastic Constant C66all = ${C66all} ${cunits}"

print "Elastic Constant C14all = ${C14all} ${cunits}"
print "Elastic Constant C15all = ${C15all} ${cunits}"
print "Elastic Constant C16all = ${C16all} ${cunits}"

print "Elastic Constant C24all = ${C24all} ${cunits}"
print "Elastic Constant C25all = ${C25all} ${cunits}"
print "Elastic Constant C26all = ${C26all} ${cunits}"

print "Elastic Constant C34all = ${C34all} ${cunits}"
print "Elastic Constant C35all = ${C35all} ${cunits}"
print "Elastic Constant C36all = ${C36all} ${cunits}"

print "Elastic Constant C45all = ${C45all} ${cunits}"
print "Elastic Constant C46all = ${C46all} ${cunits}"
print "Elastic Constant C56all = ${C56all} ${cunits}"

print "========================================="
print "Average properties for a cubic crystal"
print "========================================="

print "Bulk Modulus = ${bulkmodulus} ${cunits}"
print "Shear Modulus 1 = ${shearmodulus1} ${cunits}"
print "Shear Modulus 2 = ${shearmodulus2} ${cunits}"
print "Poisson Ratio = ${poissonratio}"
"""


if __name__ == "__main__":
    # generate and enter an output directory
    os.mkdir("./out")
    os.chdir("./out")

    # write the init template
    settings = {"structure_path": CONFIGURATION["structure_path"]}
    write_lammps_inputs(
        ".", 
        init_template, 
        settings=settings,
        script_filename="init.mod",
    )
    
    # write the potential template
    settings = {
        "pair_style": CONFIGURATION["pair_style"],
        "potential_path": CONFIGURATION["potential_path"],
        "atom_types": CONFIGURATION["atom_types"],
    }
    write_lammps_inputs(
        ".",
        potential_template,
        settings=settings,
        script_filename="potential.mod",
    )

    # write the displace template
    with open("displace.mod", "w") as f:
        f.write(displace_template)

    # write the input script
    with open("in.lammps", "w") as f:
        f.write(input_script)

    # run the calculation
    cmd = "$LAMMPS_SERIAL_BIN -in in.lammps >/dev/null"
    print("Running the calculation...")
    os.system(cmd)
    print("Completed the calculation.")

# CyberGridSim

This repository contains the framework and topologies used in:

*Shedding Light on Inconsistencies in Grid Cybersecurity: Disconnects and Recommendations*

B. Singer, A. Pandey, S. Li, L. Bauer, C. Miller, L. Pileggi, and V. Sekar. IEEE S&P 2023. To appear.

# Topologies

`Topologies/Original` are the original unmodified topologies from prior work.

`Topologies/Modified` are the more realistic modified topologies we created and additional example scenarios.

For each topology we supply both the MATPOWER and RAW file format.

## Original topologies and case names

Our work used four topologies from prior work. We keep the original filenames:

1. Synthetic Polish 2008 summer
   topology: `case3120sp` [source](https://matpower.app/manual/matpower/ExamplematpowerCases.html)
2. Synthetic South Carolina (only used for
   FDIA): `ACTIVSg500` [source](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/activsg500/)
3. Synthetic Texas: `ACTIVSg2000` [source](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/activsg2000/)
4. Synthetic Western: `ACTIVSg10k` [source](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/activsg10k/)

## Modified topologies

In our work we modified the original topologies to be more realistic. Additionally, we created three Texas scenarios.

### Modified to be realistic

`{case}_real`: Is the topology with the adjusted line and generator power bounds to be more realistic.

`{case}_real_RG`: The same as the real topology, but has responsive reserve generators. In order to run a case with
responsive reserve generation, you must run this topology. The generators with the ID's specified in the config file
have modified power boundaries.

### MadIoT scenarios

The `ACTIVSg2000_real_RG_{scenario}` cases are the additional Texas scenarios used in the study.

`scenario` has one of three options:

1. `device_emergency`: An N-6 scenario, 6 large devices are turned off

2. `load_increase_emergency_10`: Load and generation are increased by 10\%.

3. `load_decerease_emergency_10`: Load and generation are decreased by 10\%.

### Polish topology note

`case3120sp_adjusted.raw`: The original topology cascades into failure.
This topology is the original with 21 line limits doubled so the case does not fail.

# Powerflow Framework

**WARNING:**
[SUGAR](https://www.pearlstreettechnologies.com/), the solver used in the paper, is proprietary and cannot be included
in this repository. As a result, I wrote a wrapper for the [pandapower](https://www.pandapower.org/) solver (an
open-source solver), but pandapower often cannot find a solution or finds unrealistic solutions  (more details below).
As a result, the results in the paper cannot be reproduced with pandapower.
We highly recommend
purchasing proprietary
solvers such as [SUGAR](https://www.pearlstreettechnologies.com/) or [PowerWorld](https://www.powerworld.com/) to have
meaningful results.

## Setting up python environment

1. Install [Conda](https://www.anaconda.com/) if you don't already have it.
2. Create a conda environment: `conda env create -f conda_environment.yml`
3. Activate the environment: `conda activate CyberGridSim`

## Running a MadIoT experiment
This MadIoT experiment finds the minimum load increase for grid failure. For example, for the original
Texas topology we found that an attacker would need to increase load by at least 2.1% to cause a grid failure.

Run: `python -m Experiments.IncreasingMadIoT -c Configs/original_texas_no_reserves.json`

When using the PandaPower solver, the experiment should fail at 1.4% power demand increase.
The expected error should be a slack bound error.

When using the SUGAR solver, the experiment results in 2.1% (as shown in Figure 7 in the paper).

Note: The reason for the difference is that the pandapower baseline solution has an unrealistic slack power. A more
realistic solution exists, both SUGAR and PowerWorld find one with a realistic slack power. I may be misusing the
pandapower API, please let me know if there is a setting I am missing :)

## Running a random substation attack experiment

Run: `python -m Experiments.RandomSubstationAttack -n 20 -c Configs/modified_texas_reserves.json`

This experiment will randomly select 20 substations to remove from the test case and simulates the grid.
The test is random, but it has a high probability of failure. The pandapower solver has trouble determining grid
failures,
and will sometimes report success but the final state is unrealistic. When using SUGAR, this test case will almost
always
fail because 20 substations is a very dangerous attack.

## Running a power plant takeover attack

Run: `python -m Experiments.TopGeneratorsAttack -c Configs/modified_texas_reserves.json`

This runs the experiment for Finding 8 in the paper. For a varying amount of droop reserves, a
power plant takeover attack is simulated. In the simulated attack, the largest generators, starting from the 10th
largest, are sequentially shut down until the grid fails.

When running with pandapower, the simulation will report that it always only takes one generator to fail no matter the
droop reserves. This occurs because of the same slack issue seen with the MadIoT experiment. With SUGAR,
you should see as you increase droop reserves, more power plants need to be shut down to cause a grid failure.

## Running a false data injection attack (FDIA)

The FDIA attaks require MATLAB and MATPOWER. For instructions on running, please view `FDIA_Attacks/README.md`
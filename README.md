# CyberGridSim

This repository contains the framework and topologies used in:

*Shedding Light on Inconsistencies in Grid Cybersecurity: Disconnects and Recommendations*

B. Singer, A. Pandey, S. Li, L. Bauer, C. Miller, L. Pileggi, and V. Sekar. IEEE S&P 2023. To appear.

# Topologies

`Topologies/Original` are the original unmodified topologies.

`Topologies/Modified` are the more realistic modified topologies.

## Real and reserve generation topologies

`{case}_real`: Is the topology with the adjusted line and generator power bounds to be more realistic.

`{case}_real_RG`: The same as the real topology, but has responsive reserve generators. In order to run a case with
responsive reserve generation, you must run this topology. The generators with the ID's specified in the config file
have modified power boundaries.

## MadIoT scenarios
The `ACTIVSg2000_real_RG_{scenario}` cases are the additional Texas scenarios used in the study.

`device_emergency`: An N-6 scenario, 6 large devices are turned off

`load_increase_emergency_10`: Load and generation are increased by 10\%.

`load_decerease_emergency_10`: Load and generation are decreased by 10\%.

## Polish topology note

`case3120sp_adjusted.raw`: The original topology cascades into failure.
This topology is the original with 21 line limits doubled so the case does not fail.

# Powerflow Framework

**WARNING:**
[SUGAR](https://www.pearlstreettechnologies.com/), the solver used in the paper, is proprietary and cannot be included
in this repository. As a result, I wrote a wrapper for the [pandapower](https://www.pandapower.org/) solver (an
open-source solver), but pandapower cannot solve the cases when Q-limiting is enabled. As a result, the solutions become
meaningless and the results from the paper are not reproducible when using the pandapower solver. We highly recommend
purchasing proprietary
solvers such as [SUGAR](https://www.pearlstreettechnologies.com/) or [PowerWorld](https://www.powerworld.com/) to have
meaningful results.

## Setting up python environment

1. Install [Conda](https://www.anaconda.com/) if you don't already have it.
2. Create a conda environment: `conda env create -f conda_environment.yml`
3. Activate the environment: `conda activate CyberGridSim`

## Running a MadIoT experiment
Run: `python -m Experiments.IncreasingMadIoT -c Configs/original_texas_no_reserves.json`

When using the PandaPower solver, the experiment should fail at 1.4% power demand increase.
When using the SUGAR solver, the experiment results in 2.1% (as shown in Figure 7 in the paper).

Note: The reason for the difference is that the pandapower baseline solution has an unrealistic slack power.

## Running a random substation attack experiment
Run: `python -m Experiments.RandomSubstationAttack -n 20 -c Configs/modified_texas_reserves.json`

This experiment will randomly select 20 substations to remove from the test case and simulates the grid.
The test is random, but it has a high probability of failure. The pandapower solver has trouble determining grid failures,
and will sometimes report success but the final state is unrealistic. When using SUGAR, this test case will almost always
fail because 20 substations is very high.

## Running a power plant takeover attack
Run: `python -m Experiments.TopGeneratorsAttack -c Configs/modified_texas_reserves.json`

This runs the experiment for Finding 8 in the paper. For a varying amount of droop reserves, a
power plant take over attack is simulated. The attack simulated, is the largest generators (starting from 10th largest)
are sequentially shutdown until the grid fails.

When running with pandapower, the simulation will report that it always only takes one generator to fail no matter the 
droop reserves. This occurs because of the same slack issue seen with the MadIoT experiment. With SUGAR,
you should see as you increase more droop reserves, it takes more power plants to turnoff to cause a grid failure.

## Running a false data injection attack (FDIA)
The FDIA attaks require MATLAB and MATPOWER. For instructions on running, please view `FDIA_Attacks/README.md`
# CyberGridSim

This repository contains the framework and topologies used in:

*Shedding Light on Inconsistencies in Grid Cybersecurity: Disconnects and Recommendations*

B. Singer, A. Pandey, S. Li, L. Bauer, C. Miller, L. Pileggi, and V. Sekar. IEEE S&P 2023. To appear.

# Topologies

`Topologies/Original` are the original unmodified topologies.

`Topologies/Modified` are the more realistic modified topologies.

## Real and reserve generation topologies

`{case}_real`: Is the topology with the adjusted line and generator power bounds to be more realistic.

`{case}_real_RG`: Is the topology with the adjusted line and generator power bounds to be more realistic.

## MadIoT scenarios
The `ACTIVSg2000_real_RG_{scenario}` cases are the additional Texas scenarios used in the study.

`device_emergency`: An N-6 scenario, 6 large devices are turned off

`load_increase_emergency_10`: Load and generation are increased by 10\%.

`load_decerease_emergency_10`: Load and generation are decreased by 10\%.

## Polish topology note

`case3120sp_adjusted.raw`: The original topology cascades into failure.
This topology is the original with 21 line limits doubled so the case does not fail.

# Framework

The current framework was written for a proprietary tool "SUGAR". I am currently porting the code so that it only interacts with test cases, so any solver can be used.
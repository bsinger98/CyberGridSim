import argparse
from rich import print

from Simulator import GridSimulator, PowerFlowCase


def adjust_gen_params(powerflow_case: PowerFlowCase, min_droop=.05):
    generators_with_unrealistic_params = 0

    for gen in powerflow_case.generators:
        gen_reserve = min_droop * gen.Pg
        gen_unrealistic = False

        # Polish grid has generators with P below Pmin, this handles this case
        if gen.Pg < gen.Pmin:
            gen.Pmin = gen.Pg - gen_reserve
            gen.Pmax = gen.Pg + gen_reserve
            gen_unrealistic = True
        else:
            # Adjust if power reserves are too little
            if gen.Pmax - gen.Pg < gen_reserve:
                gen.Pmax = gen.Pg + gen_reserve
                gen_unrealistic = True
            if gen.Pg - gen.Pmin < gen_reserve:
                gen.Pmin = gen.Pg - gen_reserve
                gen_unrealistic = True

        if gen.Pmin < 0:
            gen.Pmin = 0

        if gen_unrealistic:
            generators_with_unrealistic_params += 1

    print(f'Generators adjusted: {generators_with_unrealistic_params}/{len(powerflow_case.generators)}')
    return


def adjust_line_params(powerflow_case: PowerFlowCase):
    # Run baseline solver to get line flows
    grid_simulator = GridSimulator(powerflow_case)
    grid_simulator.run_baseline(powerflow_case)

    overlimit_branches, _ = powerflow_case.get_devices_exceeding_limit()

    for branch in overlimit_branches:
        # A is max case
        if branch.rateA > branch.rateB and branch.rateA > branch.rateC:
            branch.rateA *= 2
        # B is max case
        elif branch.rateB > branch.rateA and branch.rateB > branch.rateC:
            branch.rateB *= 2
        # C is max case
        else:
            branch.rateC *= 2

        branch.max_rate = max(branch.rateA, branch.rateB, branch.rateC)

    print(f'Branches adjusted: {len(overlimit_branches)}/{len(powerflow_case.branches)}')
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topology_file', help='Specify path of topology file')
    args = parser.parse_args()

    # Load topology
    powerflow_case = PowerFlowCase(matpower_path=args.topology_file)

    # Adjust generator limits
    adjust_gen_params(powerflow_case)

    # Adjust line limits
    adjust_line_params(powerflow_case)
import argparse
import scipy.io
from rich import print
import json

from Simulator import GridSimulator, PowerFlowCase, PowerFlowSolver, ReserveGeneration
from Attacks import MadIoT_attack, turn_off_buses


def main(config_file_path):
    # Read config file
    config_file = open(config_file_path)
    config = json.load(config_file)

    # Load topology
    mat = scipy.io.loadmat(config['topology'], matlab_compatible=True)
    powerflow_case = PowerFlowCase(mat)

    # TODO REMOVE
    reserve_adder = ReserveGeneration(powerflow_case, config['total_agc_reserves'])
    # load_change = MadIoT_attack(powerflow_case, 1.05)
    # print(f'Load Changed: {load_change}MW')
    #
    # generation_change = reserveAdder.add_reserve_generation(powerflow_case, load_change)
    # print(f'Generation Change: {generation_change}MW')

    # solver = PowerFlowSolver()
    # new_mat = solver.run_pf(powerflow_case)
    gridSimulator = GridSimulator(powerflow_case)
    #turn_off_buses(powerflow_case, [1, 5])

    gridSimulator.run_baseline(powerflow_case)
    final_grid_state = gridSimulator.run_simulation(powerflow_case, reserve_adder)

    print(f'Final grid state: {final_grid_state}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file', help='Specify path of configuration file')
    args = parser.parse_args()

    main(args.config_file)

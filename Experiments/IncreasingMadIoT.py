"""
For a given test case, this script determines the smallest MadIoT attack that will cause the test case to fail.
"""

import argparse
import csv
from rich import print
import json

from Attacks import MadIoT_attack
from Simulator import PowerFlowCase, GridSimulator, ReserveGeneration, SimulatorResultStatus


def main(config_file_path):
    # Read config file
    config_file = open(config_file_path)
    config = json.load(config_file)

    # Load topology
    powerflow_case = PowerFlowCase(matpower_path=config['topology'])

    # Setup Simulator
    grid_simulator = GridSimulator(powerflow_case)
    reserve_adder = ReserveGeneration(powerflow_case, config['total_agc_reserves'])
    grid_simulator.run_baseline(powerflow_case)

    # Data recording
    results = []

    # Run cascading analysis
    stepping_finished = False
    attack_load_factor = 1.0
    load_factor_stepping = 0.001

    ### MadIoT Stepping Loop
    while not stepping_finished:
        print(f'Running Step: {attack_load_factor}')

        # Add MadIoT load to test case
        load_change = MadIoT_attack(powerflow_case, attack_load_factor)
        # Simulate reserve generation on test case
        generation_change = reserve_adder.add_reserve_generation(powerflow_case, load_change)
        # Run Simulation
        sim_status = grid_simulator.run_simulation(powerflow_case, reserve_adder)

        if sim_status != SimulatorResultStatus.SUCCESS:
            stepping_finished = True

        # Record Measurements
        results.append([attack_load_factor, load_change, generation_change, powerflow_case.total_generation_mw(),
                        powerflow_case.total_load_mw(), sim_status])

        # Change load factor and rerun
        attack_load_factor += load_factor_stepping

    # Save Simulation Data
    with open('results/' + f'{config["name"]}_MadIoT_Increasing.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['Load Factor', 'Load Change (MW)', 'Generation Change (MW)',
                            'Total Generation (MW)', 'Total Load (MW)',
                            'Final Sim State'])
        for res in results:
            csvwriter.writerow(res)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file', help='Specify path of configuration file')
    args = parser.parse_args()

    main(args.config_file)

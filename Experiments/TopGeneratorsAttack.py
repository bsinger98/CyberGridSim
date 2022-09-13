import argparse
import csv
import json

from Attacks import highest_ppt_attack
from Simulator import GridSimulator, PowerFlowCase, ReserveGeneration, SimulatorResultStatus


def run_high_power_ppt(powerflow_case: PowerFlowCase, grid_simulator: GridSimulator, reserve_adder: ReserveGeneration):
    """
    For a given test case, this script determines the number of generators that can be turned to cause failure occurs.
    The generators are sequentially selected from largest to smallest power output.
    An offset can be supplied to start from Xth largest generator.
    """
    # Run baseline
    grid_simulator.run_baseline(powerflow_case)

    grid_failed = False
    gen_offset = 10
    number_of_gens_to_turnoff = 1
    required_gens = 1
    while not grid_failed:
        # Turn off highest generator (modification is persistent so number_of_gens_to_turnoff should always be 1
        highest_ppt_attack(powerflow_case, reserve_adder, number_of_gens_to_turnoff, gen_offset=gen_offset)

        # Run simulation
        sim_state = grid_simulator.run_simulation(powerflow_case, reserve_adder)

        if sim_state != SimulatorResultStatus.SUCCESS:
            grid_failed = True
        required_gens += 1

    required_gens -= 1
    print(f'Total Gens Required for Failure: {required_gens}')

    return required_gens, sim_state


def ppt_with_varying_droop(config, droop_start=0, droop_step=.1, droop_max=.5):
    # Load topology
    powerflow_case = PowerFlowCase(matpower_path=config['topology'])

    # Setup Simulator
    grid_simulator = GridSimulator(powerflow_case)
    reserve_adder = ReserveGeneration(powerflow_case, config['total_agc_reserves'])
    grid_simulator.run_baseline(powerflow_case)

    # Keep adding more droop
    results = []
    while droop_start <= droop_max:
        # Reload topology
        powerflow_case = PowerFlowCase(matpower_path=config['topology'])
        # Adjust droop limit
        grid_simulator.droop_limit = droop_start
        reserve_adder.droop_ramp = droop_start
        # Rerun simulation
        required_gens, final_sim_state = run_high_power_ppt(powerflow_case, grid_simulator, reserve_adder)
        results.append([droop_start, required_gens, final_sim_state])

        droop_start += droop_step

    # Save data
    sim_name = config['name']
    sim_type = 'PPTDroop'
    with open('results/' + f'{sim_name}_{sim_type}.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['Droop_limit', 'Gens_for_failure', 'Failure_state'])
        for res in results:
            csvwriter.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file', help='Specify path of configuration file')
    args = parser.parse_args()

    # Read config file
    config_file = open(args.config_file)
    config = json.load(config_file)

    ppt_with_varying_droop(config)

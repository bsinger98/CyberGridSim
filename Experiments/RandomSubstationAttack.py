import argparse
import json
import random

from Simulator import PowerFlowCase, GridSimulator, ReserveGeneration, PowerFlowSolverDidNotConverge, SimulatorResultStatus


def run_random_ukraine(config, num_substations):
    # Load topology
    powerflow_case = PowerFlowCase(matpower_path=config['topology'])

    # Setup Simulator
    grid_simulator = GridSimulator(powerflow_case)
    reserve_adder = ReserveGeneration(powerflow_case, config['total_agc_reserves'])

    # Select the random substations
    buses_to_turn_off = []
    for substation_num in range(0, num_substations):
        choosing_num = True
        while choosing_num:
            random_num = random.randrange(0, len(powerflow_case.buses))
            chosen_bus = powerflow_case.buses[random_num]
            # Not already selected and not a slack bus
            if chosen_bus.bus_number not in buses_to_turn_off and chosen_bus not in powerflow_case.slack_bus_numbers:
                buses_to_turn_off.append(chosen_bus.bus_number)
                choosing_num = False

    # Turn off buses
    powerflow_case.turn_off_buses(buses_to_turn_off)

    # Run baseline after buses are removed
    try:
        grid_simulator.run_baseline(powerflow_case)
    except PowerFlowSolverDidNotConverge:
        return SimulatorResultStatus.NON_CONVERGENCE_FAILURE

    # Run simulation
    result = grid_simulator.run_simulation(powerflow_case, reserve_adder)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file', help='Specify path of configuration file')
    parser.add_argument('-n', '--number_of_substations', help='Specify number of substations to turn off', type=int)
    args = parser.parse_args()

    # Read config file
    config_file = open(args.config_file)
    config = json.load(config_file)

    res = run_random_ukraine(config, args.number_of_substations)
    print(f'Result of simulation: {res}')

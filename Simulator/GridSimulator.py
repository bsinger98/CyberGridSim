import networkx as nx
from enum import Enum

from .PandapowerPowerFlowSolver import PandapowerPowerFlowSolver, PowerFlowSolverDidNotConverge
from .PowerFlowCase import PowerFlowCase
from . ReserveGeneration import ReserveGeneration

from GridComponents import Bus, Branch


class SimulatorResultStatus(Enum):
    SUCCESS = 1
    SLACK_BOUND_FAILURE = 2
    CASCADING_NON_CONVERGENCE_FAILURE = 3
    NON_CONVERGENCE_FAILURE = 4
    SLACK_ISLANDING_FAILURE = 5


class GridSimulator:

    def __init__(self, droop_limit=.05, slack_ramp_limit=.1, agc_limit=.1, total_agc_reserves=0):
        """
        :param droop_limit:
        :param slack_ramp_limit:
        :param agc_limit:
        :param total_agc_reserves: Amount of AGC reserves to simulate in MW
        """
        self.ranBaseline = False

        # Reserve generation assumptions
        self.droop_limit = droop_limit
        self.total_agc_reserves = total_agc_reserves
        self.agc_limit = agc_limit
        self.slack_ramp_limit = slack_ramp_limit

        self.powerflow_solver = PandapowerPowerFlowSolver()

        return

    # Must run a baseline for each case before running
    def run_baseline(self, powerflow_case: PowerFlowCase):
        # Use pandapower to solve case
        self.powerflow_solver.run_pf(powerflow_case)

        if len(powerflow_case.slack_generators) == 0:
            raise Exception('Error: Could not find a slack generator for the test case')

        # Determine slack power
        self.baseline_slack_p, self.baseline_slack_pmin, self.baseline_slack_pmax = powerflow_case.get_slack_powers()

        # Determine slack power bounds
        self.slack_limited_pmax = self.baseline_slack_p + self.baseline_slack_p * self.slack_ramp_limit
        self.slack_limited_pmin = self.baseline_slack_p - self.baseline_slack_p * self.slack_ramp_limit
        self.slack_power_bound = (self.slack_limited_pmax + self.slack_limited_pmin) / 2

        # Select AGC generators
        self.agc_gens = []
        sorted_gens = sorted(powerflow_case.active_generators, key=lambda gen: gen.Pg, reverse=True)
        agc_gen_added = 0
        for gen in sorted_gens:
            if agc_gen_added >= self.total_agc_reserves:
                break
            # Skip generator if generator is off or generator is responsive reserve generation
            if not gen.active or gen.ckt == 'RG':
                continue

            self.agc_gens.append(gen.bus_number)
            agc_gen_added += ((gen.Pg * self.agc_limit) - (gen.Pg * self.droop_limit)) * powerflow_case.baseMVA

        # Create graph of grid for contingency analysis
        self.grid_graph = nx.MultiGraph()

        # Gather total power on each bus
        bus_powers = {}
        for gen in powerflow_case.active_generators:
            if gen.bus_number not in bus_powers:
                bus_powers[gen.bus_number] = 0
            bus_powers[gen.bus_number] += gen.Pg
        for load in powerflow_case.loads:
            if load.bus_number not in bus_powers:
                bus_powers[load.bus_number] = 0
            bus_powers[load.bus_number] -= load.Pd
        for slack in powerflow_case.slack_generators:
            if slack.bus_number not in bus_powers:
                bus_powers[slack.bus_number] = 0
            bus_powers[slack.bus_number] += slack.Pg

        # Add nodes with power details
        nodes = []
        for bus in powerflow_case.buses:
            bus_power = 0
            if bus.bus_number in bus_powers:
                bus_power = bus_powers[bus.bus_number]
            self.grid_graph.add_node(bus.bus_number, power=bus_power)

        # Add edges
        for branch in powerflow_case.active_branches:
            self.grid_graph.add_edge(branch.from_bus, branch.to_bus, key=f'line_{branch.branch_id}')

        self.ranBaseline = True

    def single_islands_created_by_contingencies(self, bus_contingencies: list[Bus], branch_contingencies: list[Branch]):
        islands_created = []
        power_dropped = 0

        island_checking_graph = self.grid_graph.copy()

        # remove buses and lines from graph
        for branch in branch_contingencies:
            if island_checking_graph.has_edge(branch.from_bus, branch.to_bus, key=f'line_{branch.branch_id}'):
                island_checking_graph.remove_edge(branch.from_bus, branch.to_bus, key=f'line_{branch.branch_id}')
        for bus in bus_contingencies:
            island_checking_graph.remove_node(bus)

        for island in nx.connected_components(island_checking_graph):
            if len(island) == 1:
                island_bus = next(iter(island))
                bus_p = island_checking_graph.nodes[island_bus]['power']
                power_dropped += bus_p
                islands_created.extend(island)

        return islands_created, power_dropped

    def run_simulation(self, powerflow_case: PowerFlowCase, reserve_adder: ReserveGeneration, slack_loop_limit = 10,
                       enable_slack_limits=True):
        if not self.ranBaseline:
            raise Exception("Error: you have to run a baseline before simulating grid")

        sim_result_status = SimulatorResultStatus.SUCCESS

        # Stores the components that have failed
        branch_contingency = []
        gen_contingency = []
        bus_contingency = []

        # Reset cascading variables
        cascading_finished = False
        cascading_loop_occurred = False
        simulation_converged = True
        slack_limit_reached = False

        overlimit_branches = []
        total_components_failed = 0
        line_failures = 0

        ### Cascading Loop
        while not cascading_finished:
            num_component_failed_old = len(branch_contingency) + len(bus_contingency)

            # Setup slack loop variables
            slack_loop_finished = False
            prev_slack_power = -1000
            slack_loop_count = 0
            slack_loop_limit = slack_loop_limit

            ### Slack Loop ###
            while not slack_loop_finished:
                bus_islands, power_dropped = self.single_islands_created_by_contingencies(bus_contingency,
                                                                                          branch_contingency)
                bus_contingency.extend(bus_islands)

                # Adjust powerflow_case to handle dropped power
                reserve_adder.add_reserve_generation(powerflow_case, power_dropped)

                # Turn off devices that have failed
                for branch in branch_contingency:
                    branch.turn_off()
                powerflow_case.turn_off_buses(bus_contingency)

                # Solve equations
                try:
                    # Use pandapower to solve case
                    self.powerflow_solver.run_pf(powerflow_case)
                except PowerFlowSolverDidNotConverge:
                    simulation_converged = False
                    break

                simulation_converged = True

                if not enable_slack_limits:
                    slack_loop_finished = True
                    break

                # Get slack powers
                total_slack_p, _, _ = powerflow_case.get_slack_powers()

                # If slack in bounds, finish loop
                if self.slack_limited_pmax > total_slack_p > self.slack_limited_pmin:
                    slack_loop_finished = True
                    break

                # If generation change hasn't changed end loop
                if prev_slack_power == total_slack_p:
                    slack_loop_finished = True
                    break

                if slack_loop_count == slack_loop_limit:
                    slack_limit_reached = True
                    break
                else:
                    slack_limit_reached = False

                delta_slack = 0
                # Slack out of bounds, redo but with higher generation output
                if total_slack_p > self.slack_limited_pmax:
                    delta_slack += 1.1 * (total_slack_p - self.baseline_slack_p)
                else:
                    delta_slack += 1.1 * (total_slack_p - self.baseline_slack_p)

                if 0 < delta_slack < .5:
                    delta_slack = .5
                if -.5 < delta_slack < 0:
                    delta_slack = -.5

                # Adjust generation to get slack in bounds
                reserve_adder.add_reserve_generation(powerflow_case, delta_slack)

                prev_slack_power = total_slack_p
                slack_loop_count += 1

            # Check Contingencies
            overlimit_branches, overlimit_generators = powerflow_case.get_devices_exceeding_limit()
            no_contingencies = True
            if len(overlimit_branches) > 0 or len(overlimit_generators) > 0:
                no_contingencies = False

            # Add to the set of branch contingencies
            for ele in overlimit_branches:
                branch_contingency.append(ele)

            for ele in overlimit_generators:
                bus_contingency.append(ele)

            num_component_failed = len(branch_contingency) + len(bus_contingency)
            line_failures += len(branch_contingency)

            if num_component_failed == num_component_failed_old or no_contingencies:
                cascading_finished = True

            if not simulation_converged or slack_limit_reached:
                cascading_finished = True
                break

            if not cascading_loop_occurred:
                self.first_line_overlimits = overlimit_branches

            cascading_loop_occurred = True

        # Save import information about simulation
        self.total_slack_p = total_slack_p
        self.failed_components = total_components_failed
        self.line_failures = line_failures

        # Slack out of bounds failure
        if total_slack_p > self.slack_limited_pmax or total_slack_p < self.slack_limited_pmin:
            sim_result_status = SimulatorResultStatus.SLACK_BOUND_FAILURE

        # Convergence failure
        if not simulation_converged:
            if cascading_loop_occurred:
                sim_result_status = SimulatorResultStatus.CASCADING_NON_CONVERGENCE_FAILURE
            else:
                sim_result_status = SimulatorResultStatus.NON_CONVERGENCE_FAILURE

        if slack_limit_reached:
            sim_result_status = SimulatorResultStatus.SLACK_ISLANDING_FAILURE

        return sim_result_status

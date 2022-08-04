from classes.Bus import Bus
from classes.Branch import Branch
from classes.Generator import Generator
from classes.HelperClasses import BusType


class PowerFlowCase:

    def __init__(self, matpower_data):
        # Store original mat file to easily generate another later
        self.original_matpower_data= matpower_data

        mpc = matpower_data['mpc']

        buses = mpc['bus'][0][0]
        busNames = mpc['bus_name'][0][0]
        branches = mpc['branch'][0][0]
        generators = mpc['gen'][0][0]

        self.baseMVA = mpc['baseMVA']
        self.buses = []
        self.branches = []
        self.active_branches = []
        self.generators = []
        self.active_generators = []
        self.loads = []
        self.slack_generators = []

        # Parse buses
        for bus in buses:
            self.buses.append(Bus(bus))

        # Parse branches
        for branch_id, raw_branch in enumerate(branches):
            branch = Branch(raw_branch, branch_id)
            self.branches.append(branch)
            if branch.active:
                self.active_branches.append(branch)

        # Parse generators
        for raw_generator in generators:
            generator = Generator(raw_generator)
            self.generators.append(generator)
            # If generator is on, add it to active generators
            if generator.active:
                self.active_generators.append(generator)

        # Find slack generators
        for bus in self.buses:
            if bus.bus_type == BusType.REF:
                self.slack_generators.append(bus)

        # Find loads
        for bus in self.buses:
            if bus.bus_type == BusType.PQ:
                self.loads.append(bus)

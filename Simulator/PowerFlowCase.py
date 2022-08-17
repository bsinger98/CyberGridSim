import scipy.io

from GridComponents.Bus import Bus
from GridComponents.Branch import Branch
from GridComponents.Generator import Generator
from GridComponents.HelperClasses import BusType


class PowerFlowCase:

    def __init__(self, matpower_data):
        # Store original mat file to easily generate another later
        self.raw_matpower_data = matpower_data

        mpc = self.raw_matpower_data['mpc']

        buses = mpc['bus'][0][0]
        busNames = mpc['bus_name'][0][0]
        branches = mpc['branch'][0][0]
        generators = mpc['gen'][0][0]

        self.baseMVA = mpc['baseMVA'][0][0][0][0]
        self.buses = []
        self.branches = []
        self.active_branches = []
        self.generators = []
        self.active_generators = []
        self.loads = []
        self.slack_buses = []
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

        # Parse generators, id'd sequentially, not sure of better way to do this
        # In PSSE format, (ckt, bus_num) is unique, but matpower format does not store ckt
        gen_id = 0
        for raw_generator in generators:
            generator = Generator(gen_id, raw_generator)
            self.generators.append(generator)
            gen_id += 1
            # If generator is on, add it to active generators
            if generator.active:
                self.active_generators.append(generator)

        # Find slack buses
        for bus in self.buses:
            if bus.bus_type == BusType.REF:
                self.slack_buses.append(bus)

        # Find slack generators
        slack_bus_ids = []
        for slack in self.slack_buses:
            slack_bus_ids.append(slack.bus_number)
        for generator in self.active_generators:
            if generator.bus_number in slack_bus_ids:
                self.slack_generators.append(generator)

        # Find loads
        for bus in self.buses:
            if bus.bus_type == BusType.PQ:
                self.loads.append(bus)

    def export(self, path):
        # Update internal matpower data
        mpc = self.raw_matpower_data['mpc']

        buses = mpc['bus'][0][0]
        branches = mpc['branch'][0][0]
        generators = mpc['gen'][0][0]

        # Update buses
        for i, _ in enumerate(buses):
            buses[i] = self.buses[i].export()

        # Update branches
        for i, _ in enumerate(branches):
            branches[i] = self.branches[i].export()

        # Update gens
        for i, _ in enumerate(generators):
            generators[i] = self.generators[i].export()

        scipy.io.savemat(path, self.raw_matpower_data)

    def convert_mw_to_base(self, mw_to_convert):
        return mw_to_convert / self.baseMVA

    def convert_base_to_mw(self, base_units_to_convert):
        return base_units_to_convert * self.baseMVA

import scipy.io
import numpy as np

from GridComponents.Bus import Bus
from GridComponents.Branch import Branch
from GridComponents.Generator import Generator
from GridComponents.HelperClasses import BusType


class PowerFlowCase:

    def __init__(self, matpower_data=None, matpower_path=None):
        # Argument exceptions
        if matpower_data is None and matpower_path is None:
            raise Exception('Must supply either matpower data or path')

        if matpower_data is not None and matpower_path is not None:
            raise Exception('Cannot supply both path and data')

        # Read from path if path is supplied
        if matpower_path is not None:
            matpower_data = scipy.io.loadmat(matpower_path, matlab_compatible=True)

        # Store original mat file to easily generate another later
        self.raw_matpower_data = matpower_data

        mpc = self.raw_matpower_data['mpc']

        buses = mpc['bus'][0][0]
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

    def get_slack_powers(self):
        slack_p = 0
        slack_pmin = 0
        slack_pmax = 0
        for slack_gen in self.slack_generators:
            slack_p += slack_gen.Pg
            slack_pmin += slack_gen.Pmin
            slack_pmax += slack_gen.Pmax

        return slack_p, slack_pmin, slack_pmax

    def total_generation_mw(self):
        total_generation_power = 0
        for gen in self.active_generators:
            total_generation_power += gen.Pg

        return self.convert_base_to_mw(total_generation_power)

    def total_load_mw(self):
        total_load = 0
        for load in self.loads:
            total_load += load.Pd

        return self.convert_base_to_mw(total_load)

    def get_devices_exceeding_limit(self):
        overlimit_branches = []
        overlimit_generators = []

        # TODO get generators exceeding voltage limit
        # allowedVmax = 1.3
        # allowedVmin = 0.8
        # for gen in self.active_generators:

        # for branch in self.active_branches:
        return overlimit_branches, overlimit_generators

    def export(self, path):
        # Update internal matpower data
        mpc = self.raw_matpower_data['mpc']

        buses = mpc['bus'][0][0]
        branches = mpc['branch'][0][0]
        generators = mpc['gen'][0][0]

        # Create new empty array based on buses list with same parameter dimension
        # Can't just overwrite original array, because devices might be deleted
        new_buses = np.zeros((len(self.buses), buses.shape[1]))
        # Update buses
        for i, _ in enumerate(buses):
            new_buses[i] = self.buses[i].export()
        buses = new_buses

        # Update branches
        new_branches = np.zeros((len(self.branches), branches.shape[1]))
        for i, _ in enumerate(branches):
            new_branches[i] = self.branches[i].export()
        branches = new_branches

        # Update gens
        new_generators = np.zeros((len(self.generators), generators.shape[1]))
        for i, _ in enumerate(generators):
            new_generators[i] = self.generators[i].export()
        generators = new_generators

        scipy.io.savemat(path, self.raw_matpower_data)

    def convert_mw_to_base(self, mw_to_convert):
        return mw_to_convert / self.baseMVA

    def convert_base_to_mw(self, base_units_to_convert):
        return base_units_to_convert * self.baseMVA

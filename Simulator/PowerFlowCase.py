import scipy.io
import numpy as np
from typing import List
import os

from GridComponents.Bus import Bus
from GridComponents.Branch import Branch
from GridComponents.Generator import Generator
from GridComponents.HelperClasses import BusType


class PowerFlowCase:
    refresh_file_path = 'tmp/tmp_refresh_pf_case.mat'

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
        self.buses: List[Bus] = []
        self.branches: List[Branch] = []
        self.active_branches: List[Branch] = []
        self.generators: List[Generator] = []
        self.active_generators: List[Generator] = []
        self.loads: List[Bus] = []
        self.slack_buses: List[Bus] = []
        self.slack_bus_numbers: List[int] = []
        self.slack_generators: List[Generator] = []

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
        for slack in self.slack_buses:
            self.slack_bus_numbers.append(slack.bus_number)
        for generator in self.active_generators:
            if generator.bus_number in self.slack_bus_numbers:
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

    def turn_off_buses(self, buses_to_turn_off):
        # Find the indexes for the buses to turn off
        bus_indexes = []
        for bus_to_turn_off in buses_to_turn_off:
            for index, bus in enumerate(self.buses):
                if bus.bus_number == bus_to_turn_off:
                    bus_indexes.append(index)
                    break

        # Remove buses from powerflow case
        parsed_buses = [bus for i, bus in enumerate(self.buses) if i not in bus_indexes]
        self.buses = parsed_buses

        # Remove all generators on buses to be removed
        gen_indexes_to_remove = []
        for index, gen in enumerate(self.generators):
            if gen.bus_number in buses_to_turn_off:
                gen_indexes_to_remove.append(index)
        parsed_gens = [gen for i, gen in enumerate(self.generators) if i not in gen_indexes_to_remove]
        self.generators = parsed_gens

        # Remove all branches on buses to be removed
        branch_indexes_to_remove = []
        for index, branch in enumerate(self.branches):
            if branch.from_bus in buses_to_turn_off or branch.to_bus in buses_to_turn_off:
                branch_indexes_to_remove.append(index)
        parsed_branches = [branch for i, branch in enumerate(self.branches) if i not in branch_indexes_to_remove]
        self.branches = parsed_branches

        # Refresh powerflow case because you modified bus values
        self.refresh()

    def get_devices_exceeding_limit(self):
        overlimit_branches = []
        overlimit_generators = []

        # TODO get generators exceeding voltage limit
        allowedVmax = 1.3
        allowedVmin = 0.8
        for gen in self.active_generators:
            # Find gens bus
            for bus in self.buses:
                if gen.bus_number == bus.bus_number:
                    # Check bus voltage
                    if bus.vm_pu > allowedVmax or bus.vm_pu < allowedVmin:
                        overlimit_generators.append(gen)
                    break

        for branch in self.active_branches:
            # Add overlimit lines to list
            if branch.max_rate > 0:
                if abs(branch.S_loading) > self.convert_mw_to_base(branch.max_rate):
                    if branch.from_bus not in self.slack_bus_numbers and branch.to_bus not in self.slack_bus_numbers:
                        overlimit_branches.append(branch)

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
        for i, _ in enumerate(self.buses):
            new_buses[i] = self.buses[i].export()
        mpc['bus'][0][0] = new_buses

        # Update branches
        new_branches = np.zeros((len(self.branches), branches.shape[1]))
        for i, _ in enumerate(self.branches):
            new_branches[i] = self.branches[i].export()
        mpc['branch'][0][0] = new_branches

        # Update gens
        new_generators = np.zeros((len(self.generators), generators.shape[1]))
        for i, _ in enumerate(self.generators):
            new_generators[i] = self.generators[i].export()
        mpc['gen'][0][0] = new_generators

        scipy.io.savemat(path, self.raw_matpower_data)

    def refresh(self):
        # Remove tmp file if it exists
        try:
            os.remove(self.refresh_file_path)
        except OSError:
            pass

        # Export to refresh file path
        self.export(self.refresh_file_path)

        # Reread file
        self.__init__(matpower_path=self.refresh_file_path)

    def convert_mw_to_base(self, mw_to_convert):
        return mw_to_convert / self.baseMVA

    def convert_base_to_mw(self, base_units_to_convert):
        return base_units_to_convert * self.baseMVA

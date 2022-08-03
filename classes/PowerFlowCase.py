from classes.Bus import Bus
from classes.Branch import Branch
from classes.Generator import Generator

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
        self.generators = []

        # Parse buses
        for bus in buses:
            self.buses.append(Bus(bus))

        # Parse branches
        for branch in branches:
            self.branches.append(Branch(branch))

        # Parse generators
        for generator in generators:
            self.generators.append(Generator(generator))
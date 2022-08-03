import scipy.io
from rich import print
from classes.PowerFlowCase import PowerFlowCase

# Load topology
mat = scipy.io.loadmat('Topologies/Original/MATPOWER/case3120sp.mat', matlab_compatible=True)

# Parse topology components
mpc = mat['mpc']
baseMVA = mpc['baseMVA']
buses = mpc['bus'][0][0]
busNames = mpc['bus_name'][0][0]
branches = mpc['branch'][0][0]
generators = mpc['gen'][0][0]

powerflow_case = PowerFlowCase(mat)
print('hi')





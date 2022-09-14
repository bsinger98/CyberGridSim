import os
import pandapower
from .PowerFlowCase import PowerFlowCase


class PowerFlowSolverDidNotConverge(Exception):
    pass


class PandapowerPowerFlowSolver:
    tmp_file_path = 'tmp/tmp_pf_case.mat'
    tmp_out_path = 'tmp/tmp_pf_out.mat'

    def cleanup_tmp_files(self):
        # Remove tmp files if they exists
        try:
            os.remove(self.tmp_file_path)
        except OSError:
            pass

        try:
            os.remove(self.tmp_out_path)
        except OSError:
            pass

    def run_pf(self, powerflow_case: PowerFlowCase):
        # Remove tmp file if exists
        self.cleanup_tmp_files()

        # Export new tmp file
        powerflow_case.export(self.tmp_file_path)

        # Load case
        self.pp_case = pandapower.converter.from_mpc(self.tmp_file_path)
        # Run powerflow
        try:
            pandapower.runpp(self.pp_case, max_iteration=500)
        except pandapower.powerflow.LoadflowNotConverged:
            raise PowerFlowSolverDidNotConverge

        # Add solution to powerflow case
        for index, row in self.pp_case.res_bus.iterrows():
            powerflow_case.buses[index].update_from_solution(row['vm_pu'], row['va_degree'])

        # Calculate line loadings
        for line in powerflow_case.active_branches:
            line.calc_line_loading(powerflow_case.buses)

import os
import pandapower
import scipy
from .PowerFlowCase import PowerFlowCase


class PowerFlowSolverDidNotConverge(Exception):
    pass


class PowerFlowSolver:
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

    def run_pf(self, power_flow_case):
        # Remove tmp file if exists
        self.cleanup_tmp_files()

        # Export new tmp file
        power_flow_case.export(self.tmp_file_path)

        # Load case, really slow for some reason
        self.pp_case = pandapower.converter.from_mpc(self.tmp_file_path)
        # Run powerflow
        try:
            pandapower.runpp(self.pp_case)
        except pandapower.powerflow.LoadflowNotConverged:
            raise PowerFlowSolverDidNotConverge

        # Export back to matpower
        pandapower.converter.to_mpc(self.pp_case, self.tmp_out_path)
        # Read new mat
        solved_mat = scipy.io.loadmat(self.tmp_out_path, matlab_compatible=True)

        # convert solved mat back to a powerflow case
        return PowerFlowCase(solved_mat)

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

        # Select slack
        slack_bus_idx_to_number = {}
        for index, row in self.pp_case.bus.iterrows():
            if row['name'] in powerflow_case.slack_bus_numbers:
                slack_bus_idx_to_number[index] = row['name']

        # Add slack (I don't know why pandapower doesn't auto do this)
        for slack_idx, _ in slack_bus_idx_to_number.items():
            self.pp_case.gen.loc[self.pp_case.gen['bus'] == slack_idx, 'slack'] = True

        # Run powerflow
        try:
            pandapower.runpp(self.pp_case, max_iteration=500, enforce_q_lims=True)
        except pandapower.powerflow.LoadflowNotConverged:
            raise PowerFlowSolverDidNotConverge

        # Add solution to powerflow case
        for index, row in self.pp_case.res_bus.iterrows():
            powerflow_case.buses[index].update_from_solution(row['vm_pu'], row['va_degree'])

        # Update slack results
        self.pp_case.gen['p_mw'] = self.pp_case.res_gen['p_mw']
        slack_gens = self.pp_case.gen.loc[self.pp_case.gen['slack'] == True]
        for _, slack_gen in slack_gens.iterrows():
            slack_number = slack_bus_idx_to_number[int(slack_gen['bus'])]
            for case_slack_gen in powerflow_case.slack_generators:
                if case_slack_gen.bus_number == slack_number:
                    case_slack_gen.Pg = slack_gen['p_mw']

        # Calculate line loadings
        for line in powerflow_case.active_branches:
            line.calc_line_loading(powerflow_case.buses)

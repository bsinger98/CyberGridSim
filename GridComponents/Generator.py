import numpy as np

class Generator:

    def __init__(self, raw_gen_data):
        self.bus_number = raw_gen_data[0]
        self.Pg = raw_gen_data[1]
        self.Qg = raw_gen_data[2]
        self.Qmax = raw_gen_data[3]
        self.Qmin = raw_gen_data[4]
        self.Vg = raw_gen_data[5]
        self.mBase = raw_gen_data[6]
        # If status > 0, on else off
        self.status = raw_gen_data[7]
        self.active = raw_gen_data[7] > 0
        self.Pmax = raw_gen_data[8]
        self.Pmin = raw_gen_data[9]
        self.Pc1 = raw_gen_data[10]
        self.Pc2 = raw_gen_data[11]
        self.Qc1min = raw_gen_data[12]
        self.Qc1max = raw_gen_data[13]
        self.Qc2min = raw_gen_data[14]
        self.Qc2max = raw_gen_data[15]
        self.agc_ramp_rate = raw_gen_data[16]
        self.ten_min_reserves_ramp_rate = raw_gen_data[17]
        self.thirty_min_reserves_ramp_rate = raw_gen_data[18]
        self.reactive_power_ramp_rate = raw_gen_data[19]
        self.APF = raw_gen_data[20]

    def export(self):
        return np.array([self.bus_number, self.Pg, self.Qg, self.Qmax, self.Qmin, self.Vg,
                         self.mBase, self.status, self.Pmax, self.Pmin, self.Pc1, self.Pc2,
                         self.Qc1min, self.Qc1max, self.Qc2min, self.Qc2max, self.agc_ramp_rate,
                         self.ten_min_reserves_ramp_rate, self.thirty_min_reserves_ramp_rate,
                         self.reactive_power_ramp_rate, self.APF])

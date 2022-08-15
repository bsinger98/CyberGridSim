import numpy as np

from classes.HelperClasses import BusType

class Bus:
    def __init__(self, raw_bus_data):
        self.bus_number = raw_bus_data[0]
        self.bus_type = BusType(raw_bus_data[1])
        self.Pd = raw_bus_data[2]
        self.Qd = raw_bus_data[3]
        self.Gs = raw_bus_data[4]
        self.Bs = raw_bus_data[5]
        self.area_num = raw_bus_data[6]
        self.Vm = raw_bus_data[7]
        self.Va = raw_bus_data[8]
        self.baseKV = raw_bus_data[9]
        self.zone = raw_bus_data[10]
        self.maxVm = raw_bus_data[11]
        self.minVm = raw_bus_data[12]

    def export(self):
        return np.array([self.bus_number, self.bus_type.value, self.Pd, self.Qd, self.Gs, self.Bs,
                         self.area_num, self.Vm, self.Va, self.baseKV, self.zone, self.maxVm,
                         self.minVm])

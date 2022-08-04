class Branch:
    def __init__(self, raw_bus_data, branch_id):
        self.from_bus = raw_bus_data[0]
        self.to_bus = raw_bus_data[1]
        self.r = raw_bus_data[2]
        self.x = raw_bus_data[3]
        self.b = raw_bus_data[4]
        self.rateA = raw_bus_data[5]
        self.rateB = raw_bus_data[6]
        self.rateC = raw_bus_data[7]
        self.tap = raw_bus_data[8]
        self.shift = raw_bus_data[9]
        # If status > 0, on else off
        self.active = raw_bus_data[10] > 0
        self.min_angle_diff = raw_bus_data[11]
        self.max_angle_diff = raw_bus_data[12]

        self.branch_id = branch_id

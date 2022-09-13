import numpy as np
import math


class BranchType(enumerate):
    LINE = 1
    XFMR = 2


class Branch:
    @staticmethod
    def calc_pq(v_r, v_i, i_r, i_i):
        p = v_r * i_r + v_i * i_i
        q = v_i * i_r - v_r * i_i
        return p, q

    @staticmethod
    def calc_g_b(r, x):
        G_pu = r/(r**2+x**2)
        B_pu = -x/(r**2+x**2)
        return G_pu, B_pu

    @staticmethod
    def calc_mag(real, imag):
        mag = (real**2 + imag**2)**0.5
        return mag

    @staticmethod
    def calc_ang(real, imag):
        ang = math.atan2(imag, real)*180./math.pi
        return ang

    def __init__(self, raw_bus_data, branch_id):
        self.from_bus = raw_bus_data[0]
        self.to_bus = raw_bus_data[1]
        self.r = raw_bus_data[2]
        self.x = raw_bus_data[3]
        self.b = raw_bus_data[4]
        self.rateA = raw_bus_data[5]
        self.rateB = raw_bus_data[6]
        self.rateC = raw_bus_data[7]
        self.max_rate = max(self.rateA, self.rateB, self.rateC)
        self.tap = raw_bus_data[8]
        self.shift = raw_bus_data[9]
        # If status > 0, on else off
        self.status = raw_bus_data[10]
        self.active = raw_bus_data[10] > 0
        self.min_angle_diff = raw_bus_data[11]
        self.max_angle_diff = raw_bus_data[12]

        self.branch_id = branch_id

        self.P_loading = 0
        self.Q_loading = 0
        self.S_loading = 0
        self.P_from = 0
        self.Q_from = 0

        if self.tap == 0 or self.tap == 1:
            self.type = BranchType.LINE
        else:
            self.type = BranchType.XFMR

    def turn_off(self):
        self.status = 0
        self.active = False

    def calc_line_loading(self, buses):
        if self.active:
            if self.type == BranchType.LINE:
                self.calc_line_loading_line(buses)
            else:
                self.calc_line_loading_xfmr(buses)

    def calc_line_loading_line(self, buses):
        # Find from bus
        from_bus = None
        for bus in buses:
            if self.from_bus == bus.bus_number:
                from_bus = bus
                break

        # Find to bus
        to_bus = None
        for bus in buses:
            if self.to_bus == bus.bus_number:
                to_bus = bus
                break

        vv = 1. / (self.r * self.r + self.x * self.x)
        from_ir = ((from_bus.vr - to_bus.vr) * self.r + (from_bus.vi - to_bus.vi) * self.x) * vv - (
                    self.b / 2) * from_bus.vi
        from_ii = ((from_bus.vi - to_bus.vi) * self.r - (from_bus.vr - to_bus.vr) * self.x) * vv + (
                    self.b / 2) * from_bus.vr
        to_ir = -((from_bus.vr - to_bus.vr) * self.r + (from_bus.vi - to_bus.vi) * self.x) * vv - (
                    self.b / 2) * to_bus.vi
        to_ii = -((from_bus.vi - to_bus.vi) * self.r - (from_bus.vr - to_bus.vr) * self.x) * vv + (
                    self.b / 2) * to_bus.vr
        #
        (P_from, Q_from) = self.calc_pq(from_bus.vr, from_bus.vi, from_ir, from_ii)
        (P_to, Q_to) = self.calc_pq(to_bus.vr, to_bus.vi, to_ir, to_ii)
        (self.P_from, self.Q_from) = (P_from, Q_from)
        (self.P_to, self.Q_to) = (P_to, Q_to)
        from_s = (P_from ** 2 + Q_from ** 2) ** 0.5
        to_s = (P_to ** 2 + Q_to ** 2) ** 0.5
        self.P_loading = max(abs(P_from), abs(P_to))
        self.Q_loading = max(abs(Q_from), abs(Q_to))
        self.S_loading = max(from_s, to_s)

    def calc_line_loading_xfmr(self, buses):
        # Find from bus
        from_bus = None
        for bus in buses:
            if self.from_bus == bus.bus_number:
                from_bus = bus
                break

        # Find to bus
        to_bus = None
        for bus in buses:
            if self.to_bus == bus.bus_number:
                to_bus = bus
                break

        # Calculate transformer loading
        (g_xfmr, b_xfmr) = self.calc_g_b(self.r, self.x)

        # Turns ration square
        tr2 = self.tap * self.tap

        # Admittance magnitude and angle
        y_mag = self.calc_mag(g_xfmr, b_xfmr)
        y_ang = self.calc_ang(g_xfmr, b_xfmr)

        # From bus magnitude and angle
        from_vmag = self.calc_mag(from_bus.vr, from_bus.vi)
        from_vang = self.calc_ang(from_bus.vr, from_bus.vi)

        # To bus magnitude and angle
        to_vmag = self.calc_mag(to_bus.vr, to_bus.vi)
        to_vang = self.calc_ang(to_bus.vr, to_bus.vi)

        # P from bus
        from_p = (from_vmag ** 2) * 1. / tr2 * g_xfmr - from_vmag * to_vmag * 1. / self.tap * y_mag * math.cos(
            (from_vang - to_vang - y_ang - self.shift) * math.pi / 180.)

        # Q from bus
        from_q = -(from_vmag ** 2) * 1. / tr2 * b_xfmr - from_vmag * to_vmag * 1. / self.tap * y_mag * math.sin(
            (from_vang - to_vang - y_ang - self.shift) * math.pi / 180.)

        # P to bus
        to_p = to_vmag ** 2 * g_xfmr - from_vmag * to_vmag * 1. / self.tap * y_mag * math.cos(
            (to_vang - from_vang - y_ang + self.shift) * math.pi / 180.)

        # Q to bus
        to_q = -to_vmag ** 2 * b_xfmr - from_vmag * to_vmag * 1. / self.tap * y_mag * math.sin(
            (to_vang - from_vang - y_ang + self.shift) * math.pi / 180.)

        (self.P_from, self.Q_from) = (to_p, from_q)
        (self.P_to, self.Q_to) = (from_p, from_q)
        # S for from and to bus
        from_s = self.calc_mag(to_p, to_q)
        to_s = self.calc_mag(from_p, from_q)
        self.P_loading = max(to_p, from_p)
        self.Q_loading = max(abs(to_q), abs(from_q))
        self.S_loading = max(from_s, to_s)

    def export(self):
        return np.array([self.from_bus, self.to_bus, self.r, self.x, self.b, self.rateA,
                         self.rateB, self.rateC, self.tap, self.shift, self.status, self.min_angle_diff,
                         self.max_angle_diff])

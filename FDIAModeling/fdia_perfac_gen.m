function [measure_a, idx, Vtarget_as] = ...
                fdia_perfac_gen(Vest_as,pf_astgt, ...
                            measure,idx,...
                               baseMVA, bus_as, gen_as, branch_as)


%pfa_x is power flow results calculated from Vest parameters bus_as,gen_as,branch_as
pfa_x=update_pf(Vest_as,baseMVA, bus_as,gen_as,branch_as);

% z_a = z + ha(xa) - ha(x)
[ha_x,~,~,~,~] = simulate_SCADA_meters(pfa_x,0); %select meters from power flow
[ha_xa,~,~,~,~] = simulate_SCADA_meters(pf_astgt,0);
measure_a = measure;
measure_a.PF = measure.PF + ha_xa.PF - ha_x.PF;
measure_a.PT = measure.PT + ha_xa.PT - ha_x.PT;
measure_a.PG = measure.PG + ha_xa.PG - ha_x.PG;

measure_a.QF = measure.QF + ha_xa.QF - ha_x.QF;
measure_a.QT = measure.QT + ha_xa.QT - ha_x.QT;
measure_a.QG = measure.QG + ha_xa.QG - ha_x.QG;

measure_a.Va = measure.Va + ha_xa.Va - ha_x.Va;
measure_a.Vm = measure.Vm + ha_xa.Vm - ha_x.Vm;

measure_a.Pinj = measure_a.Pinj + ha_xa.Pinj - ha_x.Pinj;
measure_a.Qinj = measure_a.Qinj + ha_xa.Qinj - ha_x.Qinj;    


bus = pf_astgt.bus;
[PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, ...
    VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN] = idx_bus;
Vtarget_as = bus(:,VM).*cos(pi / 180 * bus(:,VA))+1i*(bus(:,VM).*sin(pi / 180 * bus(:,VA)));

end
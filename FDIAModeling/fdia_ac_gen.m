function [measure_a, idx] = ...
                fdia_ac_gen(Vest_as,Vtarget_as, ...
                            measure,idx,...
                               baseMVA, bus_as, gen_as, branch_as)


%pfa_x is power flow results calculated from Vest parameters bus_as,gen_as,branch_as
pfa_x=update_pf(Vest_as,baseMVA, bus_as,gen_as,branch_as);
pfa_xa = update_pf(Vtarget_as,baseMVA, bus_as,gen_as,branch_as);     

% z_a = z + ha(xa) - ha(x)
[ha_x,~,~,~,~] = simulate_SCADA_meters(pfa_x,0); %select meters from power flow
[ha_xa,~,~,~,~] = simulate_SCADA_meters(pfa_xa,0);
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
end
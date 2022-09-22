function [measure_a, idx] = fdia_dc_gen(dA_as,measure,idx, baseMVA, bus_as, gen_as, branch_as)
%PG and Va not manipulated here
[Bbus, Bf, Pbusinj, Pfinj] = makeBdc(baseMVA, bus_as, branch_as);%note that the output B,and P is in MW, MVAR
dPinj = Bbus*dA_as./baseMVA; %this calculated injection is from "ground" to "node"
dPinj = -dPinj; %make the injection direction "bus to ground", same as measurement 
dPf = Bf*dA_as./baseMVA; %delta P(from line), direction: from bus out to line, same as measurement
dPt = -dPf;
measure_a = measure;
measure_a.Pinj = measure_a.Pinj+dPinj(idx.idx_zPinj);
table(measure.Pinj,dPinj(idx.idx_zPinj))
measure_a.PF = measure_a.PF+dPf(idx.idx_zPF);
measure_a.PT = measure_a.PT+dPt(idx.idx_zPT);
end
function [bus,gen,branch]=update_pf(V,baseMVA, bus,gen,branch)
%input: V, and grid model branch
%output: voltage, real/imag power flow at bus, gen, and branch 
% calculated by out=f(x), where f is made by input model parameter

%output of this function contains z_a=h(Xa) and z0=h(X) for all possible z 

%% get bus index lists of each type of bus
[i2e, bus, gen, branch] = ext2int(bus, gen, branch);
[ref, pv, pq] = bustypes(bus, gen);
%% build admittance matrix:
[Ybus, Yf, Yt] = makeYbus(baseMVA, bus, branch);
Ybus = full(Ybus);
Yf = full(Yf);
Yt = full(Yt);
%% update by z = Y(V)
[bus, gen, branch] = pfsoln(baseMVA, bus, gen, branch,...
    Ybus, Yf, Yt, V, ref,...
    pv, pq);
[bus, gen, branch] = int2ext(i2e, bus, gen, branch);
%% output
if nargout == 1
    updated_pf.bus = bus;
    updated_pf.gen = gen;
    updated_pf.branch = branch;
    updated_pf.baseMVA = baseMVA;
    bus = updated_pf;
end

end
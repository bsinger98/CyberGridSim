function [measure,idx,sigma,GT,V_GT] = simulate_SCADA_meters(pf_results, noise_level)
%%
%this function simulates meters by adding gaussian noise to pf solution
%output: measure: z in struct form
%idx: index of meters
%sigma: noise level, std
%GT: measure_GT
%V_GT: state variables from power flow solutions

[PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, ...
    VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN] = idx_bus;
[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, ...
    TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, ...
    ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX] = idx_brch;
[GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN, ...
    MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX, ...
    QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF] = idx_gen;
bus = pf_results.bus;
branch = pf_results.branch;
gen = pf_results.gen;
baseMVA = pf_results.baseMVA;
%% V_GT
V_GT = bus(:,VM).*cos(pi / 180 * bus(:,VA))+1i*(bus(:,VM).*sin(pi / 180 * bus(:,VA)));
%% create measurements, (empty holders)
idx.idx_zPF = [];
idx.idx_zPT = [];
idx.idx_zPG = [];
idx.idx_zVa = [];
idx.idx_zQF = [];
idx.idx_zQT = [];
idx.idx_zQG = [];
idx.idx_zVm = [];
idx.idx_zPinj = [];
idx.idx_zQinj = [];
% specify measurements
measure.PF = [];
measure.PT = [];
measure.PG = [];
measure.Va = [];
measure.QF = [];
measure.QT = [];
measure.QG = [];
measure.Vm = [];
measure.Pinj = [];
measure.Qinj = [];
% specify measurement variances
% variance is in terms of percentage
sigma.sigma_PF = [];
sigma.sigma_PT = [];
sigma.sigma_PG = [];
sigma.sigma_Va = [];
sigma.sigma_QF = [];
sigma.sigma_QT = [];
sigma.sigma_QG = [];
sigma.sigma_Vm = [];
sigma.sigma_Pinj = [];
sigma.sigma_Qinj = [];
% GT of measurements
GT.PF = [];
GT.PT = [];
GT.PG = [];
GT.Va = [];
GT.QF = [];
GT.QT = [];
GT.QG = [];
GT.Vm = [];
GT.Pinj = [];
GT.Qinj = [];

%%
measured_bus = find(bus(:,BUS_TYPE)~=NONE); %may include ZI buses, otherwise, SE not observable
%measured_bus = union(gen(:,GEN_BUS),find(bus(:,PD)+bus(:,QD)>0));%the set of all injection buses
for bus_key = measured_bus' %bus_key is index of row
    %V,P,Q injection, injection direction: from bus to ground
    bus_num = bus(bus_key,BUS_I);    
    Vm = bus(bus_key,VM);
    Pinj = bus(bus_key,PD)/baseMVA; 
    Qinj = bus(bus_key,QD)/baseMVA;
    if (bus(bus_key,BUS_TYPE)==PV)||(bus(bus_key,BUS_TYPE)==REF)
        Pinj = Pinj-sum(gen(gen(:,GEN_BUS)==bus_num,PG))/baseMVA;
        Qinj = Pinj-sum(gen(gen(:,GEN_BUS)==bus_num,QG))/baseMVA;
    end
    idx.idx_zVm = [idx.idx_zVm;bus_key];
    idx.idx_zPinj = [idx.idx_zPinj;bus_key];
    idx.idx_zQinj = [idx.idx_zQinj;bus_key];
    measure.Vm = [measure.Vm; Vm];
    measure.Pinj = [measure.Pinj; Pinj];
    measure.Qinj = [measure.Qinj; Qinj];
    sigma.sigma_Vm = [sigma.sigma_Vm;noise_level];
    sigma.sigma_Pinj = [sigma.sigma_Pinj;noise_level];%[sigma.sigma_Pinj;measurement(10)];
    sigma.sigma_Qinj = [sigma.sigma_Qinj;noise_level];%[sigma.sigma_Qinj;measurement(11)];
    GT.Vm = [GT.Vm; Vm];
    GT.Pinj = [GT.Pinj; Pinj];
    GT.Qinj = [GT.Qinj; Qinj];
    % add idx of transmission lines
    br_key_fadj = find((branch(:,F_BUS)==bus_num)&(branch(:,TAP)==0)&(branch(:,SHIFT)==0));%key of branch whose from bus is this bus
    br_key_tadj = find((branch(:,T_BUS)==bus_num)&(branch(:,TAP)==0)&(branch(:,SHIFT)==0));%key of branch whose to bus is this bus
    if length(br_key_fadj)>1
        for i_adj = 1:(length(br_key_fadj)-1)
            idx.idx_zPF = [idx.idx_zPF,br_key_fadj(i_adj)];
            idx.idx_zQF = [idx.idx_zQF,br_key_fadj(i_adj)];
        end
    end
    if length(br_key_tadj)>1
        for i_adj = 1:(length(br_key_tadj)-1)
            idx.idx_zPT = [idx.idx_zPT,br_key_tadj(i_adj)];
            idx.idx_zQT = [idx.idx_zQT,br_key_tadj(i_adj)];
        end
    end     
end
nPF = randn(length(measure.PF),1)*noise_level;
measure.PF = measure.PF+max(min(nPF,2.5*noise_level),-2.5*noise_level);
nPT = randn(length(measure.PT),1)*noise_level;
measure.PT = measure.PT+max(min(nPT,2.5*noise_level),-2.5*noise_level);
nPG = randn(length(measure.PG),1)*noise_level;
measure.PG = measure.PG+max(min(nPG,2.5*noise_level),-2.5*noise_level);
nVa = randn(length(measure.Va),1)*noise_level;
measure.Va = measure.Va+max(min(nVa,2.5*noise_level),-2.5*noise_level);
nQF = randn(length(measure.QF),1)*noise_level;
measure.QF = measure.QF+max(min(nQF,2.5*noise_level),-2.5*noise_level);
nQT = randn(length(measure.QT),1)*noise_level;
measure.QT = measure.QT+max(min(nQT,2.5*noise_level),-2.5*noise_level);
nPT = randn(length(measure.PT),1)*noise_level;
measure.PT = measure.PT+max(min(nPT,2.5*noise_level),-2.5*noise_level);
nQG = randn(length(measure.QG),1)*noise_level;
measure.QG = measure.QG+max(min(nQG,2.5*noise_level),-2.5*noise_level);
nVm = randn(length(measure.Vm),1)*noise_level;
measure.Vm = measure.Vm+max(min(nVm,2.5*noise_level),-2.5*noise_level);
nPinj = randn(length(measure.Pinj),1)*noise_level;
measure.Pinj = measure.Pinj+max(min(nPinj,2.5*noise_level),-2.5*noise_level);
nQinj = randn(length(measure.Qinj),1)*noise_level;
measure.Qinj = measure.Qinj+max(min(nQinj,2.5*noise_level),-2.5*noise_level);

idx.idx_zPF = unique(idx.idx_zPF);
idx.idx_zPT = unique(idx.idx_zPT);

Pfrom = branch(idx.idx_zPF, PF)/baseMVA;
Qfrom = branch(idx.idx_zQF, QF)/baseMVA;
measure.PF = [measure.PF; Pfrom+randn([length(Pfrom),1])*noise_level];
measure.QF = [measure.QF; Qfrom+randn([length(Qfrom),1])*noise_level];
sigma.sigma_PF = [sigma.sigma_PF;noise_level*ones([length(Pfrom),1])];
sigma.sigma_QF = [sigma.sigma_QF;noise_level*ones([length(Qfrom),1])];
GT.PF = [GT.PF; Pfrom];
GT.QF = [GT.QF; Qfrom];



Pto = branch(idx.idx_zPT, PT)/baseMVA;
Qto = branch(idx.idx_zQT, QT)/baseMVA;
measure.PT = [measure.PT; Pto+randn([length(Pto),1])*noise_level];
measure.QT = [measure.QT; Qto+randn([length(Qto),1])*noise_level];
sigma.sigma_PT = [sigma.sigma_PT;noise_level*ones([length(Pto),1])];
sigma.sigma_QT = [sigma.sigma_QT;noise_level*ones([length(Qto),1])];
GT.PT = [GT.PT; Pto];
GT.QT = [GT.QT; Qto];


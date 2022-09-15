%traditional ACSE: wls method
%close all
clear
addpath(genpath('matpower7.0/')) %add all subfolders
casename = 'case30.m';

%% simulate reality/environment
if ~(exist('measure')==1)
    disp("simulate grid enviroment and meters by power flow")
    mpc = loadcase(casename);
    %simulate truth by power flow, and SCADA meters with noise
    noise_level = 0.01; %std of gaussian noise to be added on meters
    pf_results = runpf(mpc);
    ref = find(mpc.bus(:,2)==3);
    [measure,idx,sigma,GT,V_GT] = simulate_SCADA_meters(pf_results, noise_level);
    %% add bad data (traditional)
    if_bad = 0;
    if if_bad==1
        %add one bad data
        measure.Pinj(3) = sign(measure.Pinj(3))*(1+abs(measure.Pinj(3)));
    end
end

%% attacker side:
%create imperfect grid model: topology error/inaccurate network parameter
%grid model [baseMVA, bus_as, gen_as, branch_as]
baseMVA = mpc.baseMVA;
bus_as = mpc.bus;
gen_as = mpc.gen;
branch_as0 = mpc.branch;
%create some imperfectness in network parameters
branch_as1 = mpc.branch;
branch_as1(2,11)=0;
branch_as2 = mpc.branch;
branch_as2(:,4) = branch_as0(:,4)+0.02*randn(size(branch_as0,1),1);
branch_as3 = branch_as2;
branch_as3(2,11)=0;
branch_as3(6,11)=0;

%prepare infomation: state x, 
%generate: manipulated measurement measure_a (z_a) z_a = z + ha(Xa)-ha(X)
% functin runpf returns angle in degree
Vest_as0 = V_GT; %X, estimation of the state x on attacker's server
%Vest_as = abs(V_GT); %imperfect state x
Vest_as1 = Vest_as0 + randn(length(Vest_as0),1)*0.01;
Vest_as1(1) = 1+0i; %attackers know reference bus 

%target bad case 
tgtcase_as = mpc;
tgtcase_as.bus(:,3:4) = mpc.bus(:,3:4)*0.9; %reduce load by 10%
%tgtcase_as.bus(6:10,3:4) = tgtcase_as.bus(6:10,3:4)-1;
pf_astgt = runpf(tgtcase_as);
dA_as = 3*randn(length(bus_as),1); %for FDIA DC
%dA_as = 3.*pf_results.bus(:,9);
dA_as(11:end)=0;

Instances_modes = {'perfect','perfect','DC','DC'};
Instances_cons = {'No','combined','No','combined'}; 
%Instances_modes = {'perfect','perfect','perfect','perfect','perfect',...
%    'DC','DC','DC','DC','DC'};
%Instances_cons = {'No','topology','ntwpara','state','combined',...
%    'No','topology','ntwpara','state','combined'}; 
for i = 1:length(Instances_modes)
    MODE_FDIA = Instances_modes{i}; %'DC','target AC','perfect'
    constraint = Instances_cons{i};
    Vest_as = Vest_as0;
    branch_as = branch_as0;
    if strcmp(constraint,'topology')==1
        branch_as = branch_as1;
    elseif strcmp(constraint,'ntwpara')==1
        branch_as = branch_as2;
    elseif strcmp(constraint,'state')==1
        Vest_as = Vest_as1;
    elseif strcmp(constraint,'combined')==1
        branch_as = branch_as3;
        Vest_as = Vest_as1;
    end
    if strcmp(MODE_FDIA,'target AC')
        %AC FDIA designed by certain target wrong solution Vtarget_as
        Vtarget_as = Vest_as; %target manipulate on estimate x
        Vtarget_abs = abs(Vest_as); %magnitude of wrong solution
        Vtarget_as=Vtarget_abs.*exp(1i*angle(Vest_as)*2); %Xa, the bad state that attackers want to mislead operators toward
        %Vtarget_as(2) = 0.95;
        Vtarget_as(ref)=1+0i; %attackers know reference bus  
        [measure_a, idx] = ...
            fdia_ac_gen(Vest_as,Vtarget_as, measure, idx,...
                        baseMVA, bus_as, gen_as, branch_as);
    elseif strcmp(MODE_FDIA, 'perfect')||strcmp(MODE_FDIA, 'DC')
        %well crafted fdia ac
        %Vest_as ready
        if strcmp(MODE_FDIA, 'perfect')
        [measure_a, idx, Vtarget_as] = ...
                    fdia_perfac_gen(Vest_as,pf_astgt, ...
                                measure,idx,...
                                   baseMVA, bus_as, gen_as, branch_as);

        elseif strcmp(MODE_FDIA, 'DC')
        %DC FDiA:
        %dA_as = randn(length(bus_as),1); %delta angle (radias), create some random disturb of angle        
        %dA_as = angle(Vest_as)-pf_astgt.bus(:,9)./180.*pi;
        %dA_as(ref)=0;       
        [measure_a, idx] = fdia_dc_gen(dA_as,measure,idx, baseMVA, bus_as, gen_as, branch_as);
        Vtarget_as=abs(V_GT).*exp(1i*(angle(V_GT)+dA_as)); %Xa, the bad state that attackers want to mislead operators toward
        end
    end

%% operator side: SE unit with BDD and BDI (V_SE is V_a)
baseMVA = mpc.baseMVA;
bus = mpc.bus;
gen = mpc.gen;
branch = mpc.branch;
init_option = 1;
disp("used sigma*3 in SE")
[V_SE, z_SEest, z_SEuse, if_bad, J, t_J, rW,rN]=...
                                SE_unit(baseMVA, bus, gen, branch,...
                                        measure_a, idx, sigma, ...
                                        init_option);
[V_SE_NA, z_SEest_NA, z_SEuse_NA, if_bad_NA, J_NA, t_J_NA, rW_NA,rN_NA]=...
                                SE_unit(baseMVA, bus, gen, branch,...
                                        measure, idx, sigma, ...
                                        init_option); %NA: no attack
%% operator side: SE accuracy 
% RMSE
res_x = sqrt(sum(real(V_SE-V_GT).^2+imag(V_SE-V_GT).^2)/length(bus));
res_xa = sqrt(sum(real(V_SE-Vtarget_as).^2+imag(V_SE-Vtarget_as).^2)/length(bus));
fprintf('Accuracy RMSE(x) = %1.6f, RMSE(xa) = %1.6f\n',res_x,res_xa)
fprintf('BDD %d, J %.4f,tJ %.4f\n',if_bad, J, t_J)

res_x_NA = sqrt(sum(real(V_SE_NA-V_GT).^2+imag(V_SE_NA-V_GT).^2)/length(bus));
fprintf('No attack accuracy RMSE(x) = %1.6f\n',res_x_NA)
fprintf('No attack BDD %d, J %.4f,tJ %.4f\n',if_bad_NA, J_NA, t_J_NA)

%save in instance
instance.J = J;
instance.J_NA = J_NA;
instance.res_x = res_x;
instance.res_xa = res_xa;
instance.res_x_NA = res_x_NA;
instance.t_J = t_J;
instance.MODE_FDIA = MODE_FDIA;
instance.constraint = constraint;
Instances{i} = instance;
end %end instance

%% final print of all simulated scenarios
disp("==============================\n\n")
for i = 1:length(Instances)
   instance = Instances{i};
   fprintf('%10s,%12s, %.4f, %.4f, %.4f, %.4f, %.4f \n',...
       instance.MODE_FDIA,instance.constraint,...
       instance.J, instance.J_NA,...
         instance.res_x, instance.res_xa,... 
            instance.res_x_NA); 
end


%for i = 1:10
%   fprintf('%.4f \n',Instances{i}.res_xa) 
%end 

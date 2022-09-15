function [pf_astgt,tgtcase_as] = get_attack_target_case(mpc_as,tgt_lf,vargin)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
if nargin > 2
    R_attack = vargin(1);
else
    R_attack = 1;
end
    
tgtcase_as = mpc_as;
if R_attack==1
    tgtcase_as.bus(:,3:4) = tgtcase_as.bus(:,3:4)*tgt_lf; %reduce load by 10%
else
    Nload = length(find(mpc_as.bus(:,3)>0));
    [~,load_buses]=sort(mpc_as.bus(:,3)); %sort load buses by Pload
    load_buses = flip(load_buses); %order it from maxload to minload
    K2attack = round(Nload*R_attack);
    %selected_buses_to_attack = randsample(load_buses,K2attack);
    selected_buses_to_attack = load_buses(1:K2attack);
    tgtcase_as.bus(selected_buses_to_attack,3:4) = tgtcase_as.bus(selected_buses_to_attack,3:4)*tgt_lf; %reduce load by 10%
end
pf_astgt = runpf(tgtcase_as);
end


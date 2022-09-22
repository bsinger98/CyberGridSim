function [success_prev,Vest_prev,pf_results_prev] = get_manipulated_case(mpc,...
    K_topo,K_para,...
    Mag_sparse_para,Mag_dense_para,lf,...
    shuffled_br_ids_topo,shuffled_br_ids_para,noise_level,...
    run_simulation)
%UNTITLED2 Summary of this function goes here

    
%   Detailed explanation goes here
mpc_prev = mpc;
%make topolgy different
if K_topo>0
    mpc_prev.branch = get_inaccurate_topology(mpc_prev.branch,K_topo,shuffled_br_ids_topo);
end
%make network paramter different (sparse)
if K_para>0
    [mpc_prev.branch, ~] = get_inaccurate_para_sparse(mpc_prev.branch,K_para,Mag_sparse_para,shuffled_br_ids_para);
end
%dense
if Mag_dense_para>0
    mpc_prev.branch = get_inaccurate_para_dense(mpc_prev.branch,Mag_dense_para);
end
%load factor different
mpc_prev.bus(:,3:4) = mpc_prev.bus(:,3:4)*lf; %scale load
mpc_prev.gen(:,2:3) = mpc_prev.gen(:,2:3)*lf; %scale generation
if run_simulation==1
    %create previous measurements
    pf_results_prev = runpf(mpc_prev);
    [measure_prev,idx_prev,sigma_prev,~,~] = simulate_SCADA_meters(pf_results_prev, noise_level);
    %get previous SE result (attacker can steal this solution)
    [success_prev, Vest_prev, ~, ~, ~, ~, ~, ~,~]=...
                                        SE_unit(mpc_prev.baseMVA, mpc_prev.bus, mpc_prev.gen, mpc_prev.branch,...
                                                measure_prev, idx_prev, sigma_prev, 100, ...
                                                1);%get operator's estimation at t-1
else
    success_prev = 0;
    Vest_prev = [];
end
end


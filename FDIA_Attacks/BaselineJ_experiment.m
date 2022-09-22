addpath(genpath('./matpower7.0/')) %add all subfolders

%% Case and number of trials
casename = '../Topologies/Original/MATPOWER/ACTIVSg500.mat';
N_trial = 5;

%% Run the trials
Jbase_list = [];
for i_trial = 1:N_trial
    %% Adjust load and gen
    mpc = loadcase(casename);
    %% Create measurements 
    % Simulate truth with power flow
    noise_level = 0.001; % std of gaussian noise to be added on meters
    pf_results = runpf(mpc);
    ref = find(mpc.bus(:,2)==3);
    % Simulate SCADA meters by addng noise
    [measure,idx,sigma,GT,V_GT] = simulate_SCADA_meters(pf_results, noise_level);

    %% Run state estimation on noisy data
    baseMVA = mpc.baseMVA;
    bus = mpc.bus;
    gen = mpc.gen;
    branch = mpc.branch;
    init_option = 1;
    alpha = 100;
    [success_NA, V_SE_NA, z_SEest_NA, z_SEuse_NA, if_bad_NA, J_NA, t_J_NA, rW_NA,rN_NA,gen_est_NA]=...
                                        SE_unit(baseMVA, bus, gen, branch,...
                                                measure, idx, sigma, alpha, ...
                                                init_option);
    % Store J value
    Jbase_list(i_trial) = J_NA;                                       
end
%% Data export
% Save data
save('../results/Jbase_list', 'Jbase_list')

% Plot J values
% figure,boxplot(Jbase_list);
% figure,hist(Jbase_list);
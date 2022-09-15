N_trial = 3;
Y_all = [];
S_all = [];

for i_trial = 1:N_trial
    FDIA_modelling_main;
    Y_all = [Y_all;y_J]; 
    S_all = [S_all;y_suc];
end

save(sprintf('../results/%s_Yall_%d.mat',casename(1:end-2),i_trial),'Y_all')
save(sprintf('../results/%s_Sall_%d.mat',casename(1:end-2),i_trial),'S_all')
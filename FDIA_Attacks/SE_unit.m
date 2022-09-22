function [success, V, z_est, z, if_bad, J, t_J, rW,rN,varargout]=...
    SE_unit(baseMVA, bus, gen, branch, measure, idx, sigma, alpha, init_option)
%this function runs SE and BDD (J-test) BDI(rW,rN-test)
    %% check input data integrity
%[success, measure, idx, sigma] = checkDataIntegrity(measure, idx, sigma, nbus);
%if ~success
%    error('State Estimation input data are not complete or sufficient!');
%end   
%% run state estimation
type_initialguess = init_option; % 1 - initial guess from case data
                       % 2 - flat start
                       % 3 - from input
tic
[V,baseMVA, bus, gen, branch, success, et, z, z_est, error_sqrsum, H] = ...
    run_se(baseMVA, bus, gen, branch, measure, idx, sigma, type_initialguess);
toc
%% J-test BDD
sigma_vector = [
    sigma.sigma_PF%*ones(size(idx.idx_zPF, 1), 1)
    sigma.sigma_PT%*ones(size(idx.idx_zPT, 1), 1)
    sigma.sigma_PG%*ones(size(idx.idx_zPG, 1), 1)
    sigma.sigma_Va%*ones(size(idx.idx_zVa, 1), 1)
    sigma.sigma_QF%*ones(size(idx.idx_zQF, 1), 1)
    sigma.sigma_QT%*ones(size(idx.idx_zQT, 1), 1)
    sigma.sigma_QG%*ones(size(idx.idx_zQG, 1), 1)
    sigma.sigma_Vm%*ones(size(idx.idx_zVm, 1), 1)
    sigma.sigma_Pinj%*ones(size(idx.idx_zPinj, 1), 1)
    sigma.sigma_Qinj%*ones(size(idx.idx_zQinj, 1), 1)
    ]*alpha; % NOTE: zero-valued elements of simga are skipped
sigma_square = sigma_vector.^2;

% critical value
   %chi_square_lookup(v,col+1)=t_J, 
   %col=1 90%, col=2 95%, col=3 97%, col=4 99 col=5 99.9
   %v is degree of freedom v=m-n
   %t_J is the threshold for Jtest such that if J>t_J then reject H0
load('chi_square_lookup.mat')
n_meas = length(sigma_vector);
v = n_meas - length(bus)*2;
%calculate J
J = sum((z - z_est).^2./sigma_square); %J
%hypothesis test result
disp('=================================')
fprintf('degree of freedom v=%d\n',v)
if v<100
    t_J = chi_square_lookup(v,5);%95%
    if J>=t_J
        fprintf('BDD(J-test):\n  Bad data detected in J-test, with J=%.3f, decision threshold %.3f\n', J, t_J);
        if_bad = 1;
    else
        fprintf('BDD(J-test):\n  No bad data in J-test, with J=%.3f, decision threshold %.3f\n', J, t_J);
        if_bad = 0;
    end
else
    t_J = 3;
end

if v>30
    eta1 = (J-v)/sqrt(2*v);
    eta2 = sqrt(2*J)-sqrt(2*v);
    fprintf('eta-test by J variants: \n  two standardized random variables %.3f, %.3f\n',eta1,eta2)
    if (abs(eta1)>3)&&(abs(eta2)>3)
        if v>=99
            if_bad = 1;
            disp('Detected bad data')
        end      
    else
        if v>99
            if_bad = 0;
            disp('No bad data detected')
        end       
    end
end
disp('=================================')
%% r-test
%rw:
rW =  abs(z - z_est)./sigma_vector; %weighted residual
fprintf('BDI(rW-test): %d bad data points found, decision threshold 3 (99.7%%), see rW\n',sum(rW>3));
%rN normalized residual
R = diag(sigma_vector.^2);
R_inv = diag(1./(sigma_vector.^2));
%Cov_x = inv(H'*R_inv*H);
%Cov_r1 = R - H*Cov_x*H';
Cov_r = R - (H/(H'*R_inv*H))*H'; %faster than the above 2 steps
D = diag(Cov_r);
rN = abs(z - z_est)./sqrt(D);
fprintf('BDI(rN-test): %d bad data points found, decision threshold 3 (99.7%%), see rN\n',sum(rN>3));
disp('=================================')

if max(nargout,1) > 9
    varargout{1} = gen;
end

end
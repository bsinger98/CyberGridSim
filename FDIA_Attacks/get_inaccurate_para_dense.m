function [branch_as_dense] = get_inaccurate_para_dense(branch_as0,Mag_dense_para)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
% input branch_as0 is mpc.branch
branch_as_dense = branch_as0;
dense_para_err = Mag_dense_para*randn(size(branch_as0,1),2);
branch_as_dense(:,3:4) = branch_as_dense(:,3:4)+dense_para_err;
end


function [branch_as_topo,topo_ids] = get_inaccurate_topology(branch_as0,K_topo,shuffled_br_ids_topo)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
%input: mpc.branch
%output: 
branch_as_topo = branch_as0;
topo_ids = shuffled_br_ids_topo(1:K_topo);
branch_as_topo(topo_ids,11)=0;
end


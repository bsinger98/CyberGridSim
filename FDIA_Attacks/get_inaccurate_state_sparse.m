function [Vest_as_sparse, x_ids] = get_inaccurate_state_sparse(Vest_as0,K_x,shuffled_state_ids,ref)
Vest_as_sparse = Vest_as0;
x_ids = [];
if K_x>0
    x_ids = shuffled_state_ids(1:K_x); %randsample( length(mpc.bus) , K_x ); 
    Vest_as_sparse(x_ids) = 1+0i;
    Vest_as_sparse(ref) = 1+0i; %attackers know reference bus 
end

end


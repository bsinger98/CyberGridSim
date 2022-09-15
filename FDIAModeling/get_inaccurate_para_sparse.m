function [branch_as_sparse, ntwpara_ids] = get_inaccurate_para_sparse(branch_as0,...
                                                                    K_para,Mag_sparse_para,...
                                                                    shuffled_br_ids_para)
branch_as_sparse = branch_as0;
ntwpara_ids = randsample( length(branch_as0) , K_para );
branch_as_sparse(ntwpara_ids,3:4) = branch_as_sparse(ntwpara_ids,3:4) + Mag_sparse_para;
end


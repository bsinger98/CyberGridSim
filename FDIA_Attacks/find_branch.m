function [ branch_key,is_from]=find_branch(branch,device_bus,end_bus,lineflowinfo)

from_list = branch(:,1);
to_list = branch(:,2);
match1 = (from_list==device_bus&to_list==end_bus);
match2 = (from_list==end_bus&to_list==device_bus);
match = match1|match2;
branch_key = find(match);
if length(branch_key)==0
    disp('no branch found')
end

if length(branch_key)>1
    tol = 1e-2;
    if isempty(setdiff([device_bus, end_bus],lineflowinfo(1:2)))
        rxb = branch(branch_key,3:5);
        rxb0 = lineflowinfo(3:5);
        rxb_diff = rxb - ones(length(branch_key),1)*rxb0;
        mismatch = sum(abs(rxb_diff),2);
        if min(mismatch)<tol
            branch_key = branch_key(mismatch==min(mismatch));
            if length(branch_key)>1
                branch_key = branch_key(1);
            end
            %disp('more than one branches found but matched')
        else
            branch_key = [];
            disp('no proper key found')
        end
    end
end

if match1(branch_key)==1
    is_from = 1;
else
    is_from = 0;
end

end
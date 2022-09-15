function [measure_a] = limit_write_access(measure_a,measure,shuffled_meter_ids,N_na)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

   N_meter_per = [length(measure.Pinj),length(measure.Qinj),...
       length(measure.PF), length(measure.QF),...
       length(measure.PT), length(measure.QT),...
       length(measure.Vm)]; %how many measurements in each type
   N_meter_accu = ones(1,length(N_meter_per));
   for i = 2:length(N_meter_per)
       N_meter_accu(i) = N_meter_accu(i-1) + N_meter_per(i-1);
   end
       
   all_measure_a = [measure_a.Pinj;measure_a.Qinj;...
       measure_a.PF; measure_a.QF;...
       measure_a.PT; measure_a.QT;...
       measure_a.Vm];
   all_measure = [measure.Pinj;measure.Qinj;...
       measure.PF; measure.QF;...
       measure.PT; measure.QT;...
       measure.Vm];
    na_ids = shuffled_meter_ids(1:N_na);
    all_measure_a(na_ids) = all_measure(na_ids);
    measure_a.Pinj = all_measure_a(1:N_meter_accu(2)-1);
    measure_a.Qinj = all_measure_a(N_meter_accu(2):N_meter_accu(3)-1);
    measure_a.PF = all_measure_a(N_meter_accu(3):N_meter_accu(4)-1);
    measure_a.QF = all_measure_a(N_meter_accu(4):N_meter_accu(5)-1);
    measure_a.PT = all_measure_a(N_meter_accu(5):N_meter_accu(6)-1);
    measure_a.QT = all_measure_a(N_meter_accu(6):N_meter_accu(7)-1);
    measure_a.Vm = all_measure_a(N_meter_accu(7):end);
    
end


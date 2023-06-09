% Reconstruct Images $Id: if_peep_trial02.m 1535 2008-07-26 15:36:27Z aadler $

v_injury = eidors_readdata('p1130107.get');
r_injury = mean(v_injury(:,1:10),2); % reference meas
v_treat  = eidors_readdata('p1130122.get');
r_treat  = mean(v_treat(:,1:10),2); % reference meas

i_injury = inv_solve(imdl, r_injury, v_injury);
i_treat  = inv_solve(imdl, r_treat , v_treat );

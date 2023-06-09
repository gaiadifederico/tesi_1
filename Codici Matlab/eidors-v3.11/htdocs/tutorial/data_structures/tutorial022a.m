% Create 2D model $Id: tutorial022a.m 3850 2013-04-16 18:13:39Z aadler $
clear mdl elec stim

nn= 84;     % number of nodes
ww=4;       % width = 4
conduc= 1;  % conductivity in Ohm-meters
mdl= eidors_obj('fwd_model','2D rectangle');
mdl= mdl_normalize( mdl, 0);
mdl.nodes = [floor( (0:nn-1)/ww );rem(0:nn-1,ww)]';
mdl.elems = delaunayn(mdl.nodes);
mdl.gnd_node = 1;
elec(1).nodes= [1:ww];      elec(1).z_contact= 0.01;
elec(2).nodes= nn-[0:ww-1]; elec(2).z_contact= 0.01;
stim.stim_pattern= [-1;1];
stim.meas_pattern= [-1,1];
mdl.stimulation= stim;
mdl.electrode= elec;
mdl.solve = @fwd_solve_1st_order;
mdl.system_mat = @system_mat_1st_order;

show_fem(mdl); axis('equal'); set(gca,'Ylim',[-.5,ww-.5]);
print_convert tutorial022a.png '-density 75'

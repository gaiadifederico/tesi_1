% tutorial1_create_fwd_model
% $Id: tutorial020a.m 4092 2013-05-27 22:17:28Z bgrychtol $

r_mdl= eidors_obj('fwd_model','demo resistor model');
r_mdl = mdl_normalize( r_mdl, 0);

% Geometry
r_mdl.nodes= [1,1,1;  2,2,2];
r_mdl.elems= [1,2];
r_mdl.boundary= [1,2]; 

% Define Electrodes (there is only one)
r_mdl.electrode(1).z_contact= 10; % ohms
r_mdl.electrode(1).nodes=     1;
r_mdl.gnd_node= 2;

show_fem(r_mdl); view(-12,24);
print_convert tutorial020a.png '-density 50';

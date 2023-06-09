% $Id: mk_GREIT_matrix01.m 3354 2012-07-01 21:42:05Z bgrychtol $
n_elecs = 16;
fmdl = ng_mk_cyl_models([2 2 0.2] ,[n_elecs,1],[0.1]);
fmdl.stimulation =  mk_stim_patterns(n_elecs,1,[0,1],[0,1],{'no_meas_current'}, 1);
fmdl = mdl_normalize(fmdl, 0);
img = mk_image(fmdl,1); % Homogeneous background

show_fem(fmdl); view(0,70);
print_convert mk_GREIT_matrix01a.png '-density 60'

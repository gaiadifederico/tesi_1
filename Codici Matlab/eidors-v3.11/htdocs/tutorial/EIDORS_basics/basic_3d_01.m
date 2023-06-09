% Basic 3d model $Id: basic_3d_01.m 2161 2010-04-04 20:33:46Z aadler $

fmdl= ng_mk_cyl_models(3,[15,1,1.5,2],[0.1,0,0.05]); 
show_fem(fmdl);

imdl = mk_common_model('a2c2',8); % Will replace most fields
imdl.fwd_model = fmdl;
imdl.fwd_model.stimulation = mk_stim_patterns(45,1,[0,3],[0,1],{},1);
img1 = mk_image(imdl);

show_fem(img1);

print_convert('basic_3d_01a.png','-density 60')

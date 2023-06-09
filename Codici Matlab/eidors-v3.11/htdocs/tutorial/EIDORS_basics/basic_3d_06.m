% Reconstruct Model $Id: basic_3d_06.m 2161 2010-04-04 20:33:46Z aadler $
imgr = inv_solve(imdl, vh, vi);

imgr.calc_colours.ref_level = 0; % difference imaging
imgr.calc_colours.greylev = -0.05;

show_fem(imgr);
print_convert('basic_3d_06a.png','-density 60');

show_3d_slices(imgr, [1,1.9], [0.5],[0.5]);
view(-14,13); axis tight; axis equal;
print_convert('basic_3d_06b.png','-density 60');

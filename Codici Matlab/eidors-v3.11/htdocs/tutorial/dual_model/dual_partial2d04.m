% Dual Partial $Id: dual_partial2d04.m 2749 2011-07-14 13:32:13Z aadler $

clf; levels= [inf,inf,0,1,1];

% reconstruct fine model
imgf= inv_solve(frec_mdl, vh, vi);

show_slices(imgf,levels);
print_convert dual_partial2d04a.png;

% reconstruct dual model
imgd= inv_solve(drec_mdl, vh, vi);

show_slices(imgd,levels);
print_convert dual_partial2d04b.png;


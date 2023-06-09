% Lung images
% $Id: tutorial410a.m 3340 2012-07-01 21:25:30Z bgrychtol $

% 2D Model
imdl= mk_common_model('c2t3',16);


% most EIT systems image best with normalized difference
imdl.fwd_model = mdl_normalize(imdl.fwd_model, 1);
imdl.RtR_prior= @prior_gaussian_HPF;

% electrodes start on back (dorsal), then do this
imdl.fwd_model.electrode([9:16,1:8])=  ...
   imdl.fwd_model.electrode;


subplot(221);
show_fem(imdl.fwd_model);

axis equal
print_convert tutorial410a.png;

[stim,msel] = mk_stim_patterns(16,1,[0,1],[0,1],{'no_meas_current'},1);
img.fwd_model.stimulation = stim;
img.fwd_model = mdl_normalize(img.fwd_model, 1);
opt.imgsz = [64 64];
opt.distr = 3;
opt.Nsim = 500;
opt.target_size = 0.03;
opt.target_offset = 0;
opt.noise_figure = .5; 
opt.square_pixels = 1;
imdl=mk_GREIT_model(img, 0.25, [], opt);
imdl.fwd_model.meas_select = msel;

% $Id: mk_GREIT_matrix02.m 2473 2011-03-02 20:32:23Z aadler $
opt.imgsz = [32 32];
opt.distr = 3; % non-random, uniform
opt.Nsim = 1000;
opt.target_size = 0.05; % Target size (frac of medium)
opt.noise_figure = 0.5; % Recommended NF=0.5;
imdl = mk_GREIT_model(img, 0.25, [], opt);

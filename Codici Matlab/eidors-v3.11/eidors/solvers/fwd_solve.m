function data = fwd_solve(fwd_model, img)
% FWD_SOLVE: calculate data from a fwd_model object and an image
% 
% fwd_solve can be called as
%    data= fwd_solve( img)
% or (deprecated)
%    data= fwd_solve( fwd_model, img)
%
% in each case it will call the fwd_model.solve
%                        or img.fwd_model.solve method
%
% For reconstructions on dual meshes, the interpolation matrix
%    is defined as fwd_model.coarse2fine. If required, this takes
%    coarse2fine * x_coarse = x_fine
%
% data      is a measurement data structure
% fwd_model is a fwd_model structure
% img       is an img structure
%
% Options: (not available on all solvers)
%    img.fwd_solve.get_all_meas = 1 (data.volt = all FEM nodes, but not CEM)
%    img.fwd_solve.get_all_nodes= 1 (data.volt = all nodes, including CEM)
%    img.fwd_solve.get_elec_curr= 1 (data.elec_curr = current on electrodes)
%
% Parameters:
%    fwd_model.background = constant conductivity offset added to elem_data
%    fwd_model.coarse2fine = linear mapping between img.elem_data and model parameters
%    img.params_mapping = function mapping img.elem_data to model parameters
%

% (C) 2005 Andy Adler. License: GPL version 2 or version 3
% $Id: fwd_solve.m 6307 2022-04-20 17:45:43Z aadler $

if ischar(fwd_model) && strcmp(fwd_model,'UNIT_TEST'); do_unit_test; return; end 

if nargin == 1
   img= fwd_model;
else
   warning('EIDORS:DeprecatedInterface', ...
      ['Calling FWD_SOLVE with two arguments is deprecated and will cause' ...
       ' an error in a future version. First argument ignored.']);
end
ws = warning('query','EIDORS:DeprecatedInterface');
warning off EIDORS:DeprecatedInterface


fwd_model= img.fwd_model;


fwd_model= prepare_model( fwd_model );

% TODO: This should be handled by the data_mapper
if isfield(img,'params_mapping')
%     fwd_model data is provided using a mapping function
    mapping_function= img.params_mapping.function;
    img= feval(mapping_function,img);
end
if isfield(fwd_model,'coarse2fine') && isfield(img,'elem_data')
   c2f= fwd_model.coarse2fine;
   if size(img.elem_data,1)==size(c2f,2)
%     fwd_model data is provided on coarse mesh
      img.elem_data = c2f * img.elem_data; 

      if isfield(fwd_model,'background')
          img.elem_data = img.elem_data + fwd_model.background; 
      end
   end
end

if ~isfield(fwd_model, 'electrode')
   error('EIDORS: attempting to solve on model without electrodes');
end
if ~isfield(fwd_model, 'stimulation')
   error('EIDORS: attempting to solve on model without stimulation patterns');
end

solver = fwd_model.solve;
if ischar(solver)
    solver = str2func(solver);
end

copt.fstr = 'fwd_solve';
n_frames = size(img.elem_data,2);
for frame = 1:n_frames;
   imgn = img; imgn.elem_data = imgn.elem_data(:,frame,:,:);
   copt.cache_obj = imgn;
   copt.boost_priority = -2; % fmdl evaluations are low priority
   tmp = eidors_cache(solver, {imgn}, copt);
   data(frame) = eidors_obj('data',tmp);  % create data object
end

if isa(fwd_model.solve,'function_handle')
    solver = func2str(fwd_model.solve);
else
    solver = fwd_model.solve;
end
if strcmp(solver,'eidors_default');
    solver = eidors_default('get','fwd_solve');
end
if isfield(fwd_model,'measured_quantity') && ~isfield(data,'measured_quantity')
   warning('EIDORS:MeasurementQuantityObliviousSolver',...
      ['The solver %s did not handle the requested measurement quantity properly.\n'...
       'The results may be incorrect. Please check the code to verify.'], ...
       solver);
elseif isfield(fwd_model,'measured_quantity') ... 
        && isfield(data,'measured_quantity') ...
        && ~strcmp(fwd_model.measured_quantity, data.measured_quantity)
   error('EIDORS:MeasurementQuantityDisagreement',...
       'The solver %s return measurements as %s, while %s was expected.',...
       solver, data.measured_quantity, fwd_model.measured_quantity);
end
    
warning on EIDORS:DeprecatedInterface


function mdl = prepare_model( mdl )
mdl = mdl_normalize(mdl,mdl_normalize(mdl));
if ~isfield(mdl,'elems');
    return;
end

mdl.elems  = double(mdl.elems);
mdl.n_elem = size(mdl.elems,1);
mdl.n_node = size(mdl.nodes,1);
if isfield(mdl,'electrode');
    mdl.n_elec = length(mdl.electrode);
else
    mdl.n_elec = 0;
end

function do_unit_test
img = mk_image(mk_common_model('a2c2',4));
% TODO Try other solvers
img.elem_data([1,5,9,10]) = 2;
A = [1,-1,0,0]; a=A.';
B = [0,0,1,-1]; b=B.';
G = 2; 
P = exp(0.1j);
for solv = 1:4; switch solv
    case 1; solver = 'fwd_solve_1st_order';
    case 2; solver = 'fwd_solve_2p5d_1st_order';
    case 3; solver = 'fwd_solve_higher_order';
            img.fwd_model.system_mat = @system_mat_higher_order;
            img.fwd_model.approx_type = 'tri3';
    case 4; break;
    end
    for test = 1:4; switch test
       case 1; str='reciprocity';
               mPat = {A,B}; sPat = {b,a};
       case 2; str='Gain';
               mPat = {A,A*G}; sPat = {b,b/G};
       case 3; str='Phase';
               mPat = {A,A*P}; sPat = {b,b*P};
       case 4; break
       end
       img.fwd_model.solve = solver;
       img.fwd_model.stimulation  = struct( ...
          'meas_pattern', mPat, 'stim_pattern', sPat );
        vv= getfield(fwd_solve(img),'meas');
        unit_test_cmp([solver,':',str],diff(vv),0,10*eps) 
    end
end

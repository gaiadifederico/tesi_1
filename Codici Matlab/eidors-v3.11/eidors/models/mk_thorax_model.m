function out = mk_thorax_model(str, varargin)
%MK_THORAX_MODEL FEM models of the thorax
%
% MK_THORAX_MODEL provides a shorthand to predefined thorax FEMs and 
% for using contributed models with PLACE_ELEC_ON_SURF. You may be asked
% to download missing files. 
%
% MK_THORAX_MODEL(shapestr,elec_pos, elec_shape, maxh) where:
%  shapestr    - a string specifying the underlying model.
%                Run MK_THORAX_MODEL('list_shapes') for a list.
%  elec_pos    - a vector specifying electrode positions.
%                See PLACE_ELEC_ON_SURF for details.
%  elec_shape  - a vector specifying electrode shapes.
%                See PLACE_ELEC_ON_SURF for details.
%  This usage returns a fwd_model structure.
%
% MK_THORAX_MODEL(modelstr) provides quick access to predefined models.
% Run MK_THORAX_MODEL('list') for a list. This usage returns either a 
% fwd_model or an image structure.
%
% MK_THORAX_MODEL('list_shapes') lists available thorax shapes without 
%  electrodes.
%
% MK_THORAX_MODEL('list') lists available predefined models.
%

%
% See also: PLACE_ELEC_ON_SURF, MK_LIBRARY_MODEL

% (C) 2015-2016 Bartlomiej Grychtol. License: GPL version 2 or 3
% $Id: mk_thorax_model.m 6453 2022-12-04 21:32:20Z bgrychtol $

if nargin>0 && ischar(str) 
   switch(str)
      case 'UNIT_TEST';
         do_unit_test; return;
      case 'list_shapes'
         out = list_basic_shapes; return;
      case 'list'
         out = list_predef_models; return;
   end
end

opt.fstr = 'mk_thorax_model';
out = eidors_cache(@do_mk_thorax_model,[{str}, varargin(:)'],opt);

end

function out = do_mk_thorax_model(str, elec_pos, elec_shape, maxh)

if ismember(str,list_predef_models)
   out = build_predef_model(str);
   return
end

if ~ismember(str, list_basic_shapes)
   error('Shape str "%s" not understood.',str);
end



out = build_basic_model(str);
if nargin > 1
   out = place_elec_on_surf(out,elec_pos,elec_shape,[],maxh);
   out = fix_boundary(out);
end

end

function ls = list_basic_shapes
   ls = {'male','female'};
end

function out = build_basic_model(str)
switch(str)
   case {'male', 'female'}
      out = eidors_cache(@remesh_at_model, {str});
end
end

function out = remesh_at_model(str)
   tmpnm  = tempname;
   
   stlfile = [tmpnm '.stl'];
   volfile = [tmpnm '.vol'];
   
   contrib = 'at-thorax-mesh'; file =  sprintf('%s_t_mdl.mat',str);
   load(get_contrib_data(contrib,file));
   if strcmp(str,'male')
      fmdl.nodes = fmdl.nodes - 10; % center the model
   end
   fmdl = fix_boundary(fmdl);
   STL.vertices = fmdl.nodes;
   STL.faces    = fmdl.boundary;
   stl_write(STL,stlfile);
   opt.stloptions.yangle = 55;
   opt.stloptions.edgecornerangle = 5;
   opt.meshoptions.fineness = 6;
   opt.options.meshsize = 30;
   opt.options.minmeshsize = 10;
   opt.stloptions.resthsurfcurvfac = 2;
   opt.stloptions.resthsurfcurvenable = 1;
   opt.stloptions.chartangle = 30;
   opt.stloptions.outerchartangle = 90;
   ng_write_opt(opt);
   call_netgen(stlfile,volfile);
   out=ng_mk_fwd_model(volfile,[],[],[],[]);
   delete(stlfile);
   delete(volfile);
   delete('ng.opt');
   
   out = rmfield(out,...
      {'mat_idx','np_fwd_solve','boundary_numbers'});
   
end

function mdl = fix_boundary(mdl)
    opt.elem2face  = 1;
    opt.boundary_face = 1;
    opt.inner_normal = 1;
    mdl = fix_model(mdl,opt);
    flip = mdl.elem2face(logical(mdl.boundary_face(mdl.elem2face).*mdl.inner_normal));
    mdl.faces(flip,:) = mdl.faces(flip,[1 3 2]);
    mdl.normals(flip,:) = -mdl.normals(flip,:);
    mdl.boundary = mdl.faces(mdl.boundary_face,:);
end

function ls = list_predef_models
   ls = {'adult_male_grychtol2016a_1x32'
         'adult_male_grychtol2016a_2x16'};
end

function out = build_predef_model(str)
   switch str
      case 'adult_male_grychtol2016a_1x32'
         out = mk_thorax_model_grychtol2016a('1x32_ring');
         
      case 'adult_male_grychtol2016a_2x16'
         out = mk_thorax_model_grychtol2016a('2x16_planar');
   end
end


function do_unit_test
   subplot(221)
   show_fem(mk_thorax_model('male'));
   
   subplot(222)
   show_fem(mk_thorax_model('female'));

   subplot(223)
   eth16 = 360*cumsum([0.2 0.4*ones(1,7) 0.5 0.4*ones(1,7)])/6.5 - 90; eth16 = eth16';
   eth32 = 360*cumsum([0.1 0.2*ones(1,15) 0.25 0.2*ones(1,15)])/6.45 - 90; eth32 = eth32';
   ep = eth16; ep(:,2) = 150;
   ep(17:48,1) = eth32; ep(17:48,2) = 175;
   ep(49:64,1) = eth16; ep(49:64,2) = 200;
   mdl = mk_thorax_model('male',ep,[5 0 .5],10);
   show_fem(mdl);

   subplot(224)
   mdl = mk_thorax_model('female',ep,[5 0 .5],10);
   show_fem(mdl);

   % This doens't work with mk_thorax_model
%  ng_write_opt('MSZCYLINDER',[0,0,50,0,0,60,180,5]);
%  show_fem(mk_thorax_model('male'));
   
end

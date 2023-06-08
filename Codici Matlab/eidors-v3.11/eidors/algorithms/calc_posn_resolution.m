function [br,pos]= calc_posn_resolution( img, fwd_model)
% CALC_POSN_RESOLUTION: calculate posn and resolution of a target
% [br,xpos,ypos]= calc_posn_resolution( img, fwd_model)
% 
% img - eidors img generated by a point (or small) target
% br  - Blur radius measure of resolution
% pos - [x;y] position in terms of % radius
%
% These parameters are defined in Adler & Graudo (1996),
%  IEEE T. Medical Imaging, 5:170-179, 1996.
%
% br and pos will have columns for each image in img
%
% In 3D calc_posn_resolution does a 2D z-slice in the 
% centre of the medium. This may not be appropriate

% (C) 2006 Andy Adler. Licensed under GPL version 2
% $Id: calc_posn_resolution.m 3053 2012-06-06 15:55:32Z aadler $

if nargin>=2
   img.fwd_model= fwd_model;
end

% create full 'red' image
fimg= img;
fimg.elem_data= ones(size(img.elem_data,1),1);

np= 256;
% FIXME: if the functions have an error, then npoints is changed
np_save= calc_colours('npoints');
calc_colours('npoints',np);

if     size(img.fwd_model.elems,2) == 3 % 2D
   rimg= calc_slices( img );
   fimg= calc_slices( fimg );
elseif size(img.fwd_model.elems,2) == 4 % 3D
   rimg= calc_slices( img, 1 );
   fimg= calc_slices( fimg, 1 );
else
   calc_colours('npoints',np_save);
   error('N dimensions is not 2 or 3');
end


rimg= squeeze(rimg); % for 3D case
n_imgs= size(rimg,3);
% reset npoints
calc_colours('npoints',np_save);

% Process full image to get area and x,y limits
fimg= ~isnan(fimg);
img_area= sum(fimg(:));

xfind= find(any( fimg,1));
img_xmin= min(xfind); img_xmax= max(xfind);
img_xctr= mean([img_xmin, img_xmax]);
img_xrad= [img_xmax - img_xmin]/2; % radius

yfind= find(any( fimg,1));
img_ymin= min(yfind); img_ymax= max(yfind);
img_yctr= mean([img_ymin, img_ymax]);
img_yrad= [img_ymax - img_ymin]/2; % radius

br= zeros(1,n_imgs);
pos=zeros(2,n_imgs);
for i=1:n_imgs
   img_i =       rimg(:,:,i);
   % flip so image is +
   img_i =       img_i * sign( max(img_i(:)) + min(img_i(:)));
   [img_i,idx] = sort(img_i(:));
   img_i(idx)  = cumsum(img_i .* (img_i>0));
   ha_set = img_i > max(img_i)/2;
   br(i) = sqrt(sum(ha_set)/img_area);

% create HA image
   ha_img= zeros(np,np);
   ha_img( ha_set) = 1; 
   xpos = sum( ha_img, 1);
   xpos = sum( (1:np) .* xpos ) / sum( xpos );
   xpos = (xpos - img_xctr) / img_xrad;
   ypos = sum( ha_img, 2)';
   ypos = sum( (1:np) .* ypos ) / sum( ypos );
   ypos = -(ypos - img_yctr) / img_yrad; % images y dirn is backward
   pos(:,i) = [xpos;ypos];
end
   
   
   

function [xp,yp,zp]= simulation_radmove(f_frac, radius, z0,zt);
% Radial Movement - $Id: simulation_radmove.m 2700 2011-07-13 12:26:06Z aadler $  
   rp= f_frac*radius; 
   cv= 2*pi*f_frac * 73;
   xp= rp * cos(cv);
   yp= rp * sin(cv);
   if nargin==4; zp = mean([zt,z0]); else; zp= 0; end

function out = vecnorm(x, p, dim)
% Vectorwise norm: overload for matlab pre 2017b
if nargin<2; p=2;   end
if nargin<3; dim=1; end

y = sum(x.^p, dim);
out = y.^(1/p);

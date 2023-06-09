% Demo algorithms $Id: demo_algs04.m 1576 2008-07-28 09:19:55Z aadler $

algs= get_list_of_algs;

imb.calc_colours.ref_level = 0; % select colour output
imb.calc_colours.greylev   = 0.01; % black backgnd
imb.calc_colours.backgnd   = [.5,.5,.5]; %grey

for i= 1:length(algs)
   for k= 1:4
      [img,map] = feval(algs{i}, v(k).vh, v(k).vi );

      imc= calc_colours(img, imb);
      imc(~map) = 1; % background

      imwrite(imc,colormap, sprintf('demo_algs04_%d%d.png',i,k),'png')
    end
end

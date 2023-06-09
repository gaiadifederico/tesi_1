% Simulate movement $Id: simulate_move1_02.m 2770 2011-07-14 16:54:10Z bgrychtol $
[vh,vi,xyr_pt]= simulate_2d_movement( 20, smdl,[.75,.05]);

% Show model and simulated targets
show_fem(smdl);
theta= linspace(0,2*pi,50); xr= cos(theta); yr= sin(theta);
hold on;
for i=1:length(xyr_pt)
    hh= plot(xyr_pt(3,i)*xr+ xyr_pt(1,i), ...
             xyr_pt(3,i)*yr+ xyr_pt(2,i));
    set(hh,'LineWidth',3,'Color',[0,0,1]);
    text(xyr_pt(1,i),xyr_pt(2,i),sprintf('%d',i), ...
        'HorizontalAlignment','center','FontSize',8, ...
        'Color',[0,0,1],'FontWeight','bold');
end
hold off;
axis([-1.1 1.1 -1.1 1.1]); axis equal
print_convert simulate_move1_02a.png '-density 100'

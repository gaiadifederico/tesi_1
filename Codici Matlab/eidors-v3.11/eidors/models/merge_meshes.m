function out = merge_meshes(M1,varargin)
%MERGE_MESHES - merges two meshes based on common nodes
% MERGE_MESHES(M1,M2,T) merges M2 in M1 using threshold T for detecting
%     corresponding nodes. The meshes must not overlap.
% MERGE_MESHES(M1,M2,M3,..., T) merges M2, M3, ... into M1 (individually)
%
% Note that the boundaries of the separate meshes will only be
% concatenated, as this visualises nicely. To calculate the correct
% boundary use FIND_BOUNDARY.
%
% See also FIND_BOUNDARY

% (C) Bartlomiej Grychtol and Andy Adler, 2012-2013. Licence: GPL v2 or v3
% $Id: merge_meshes.m 6454 2022-12-04 22:11:44Z bgrychtol $

if ischar(M1) && strcmp(M1,'UNIT_TEST'), run_unit_test; return; end

if nargin < 3  || isstruct(varargin{end})
   th = mean(std(M1.nodes))/length(M1.nodes);
   shapes = varargin;
else
   th = varargin{end};
   shapes = varargin(1:end-1);
end
if ~isfield(M1, 'boundary');
   M1.boundary = find_boundary(M1);
end
if ~isfield(M1, 'mat_idx')
   M1.mat_idx = {1:length(M1.elems)};
end

do_msg = length(shapes) > 1;
if do_msg, progress_msg(sprintf('Merging mesh %d/%d ... ',0,length(shapes))); end

% Use a for loop, vectorised approach can run out of memory
for i = 1:length(shapes)
   if do_msg
      progress_msg(sprintf('Merging mesh %d/%d ... ',i,length(shapes)));
   end
   l1 = length(M1.nodes);
   M2 = shapes{i};
   if ~isfield(M2, 'boundary');
      M2.boundary = find_boundary(M2);
   end
   if ~isfield(M2, 'mat_idx')
      M2.mat_idx = {1:length(M2.elems)};
   end
   % make sure boundaries are the same dimension
   if size(M1.boundary,2) == 2 && size(M2.boundary,2)==3
      % M1 is 2D, M2 is 3D
      M1.boundary = M1.elems;
   elseif size(M1.boundary,2) == 3 && size(M2.boundary,2)==2
      M2.boundary = M2.elems;
   end
   
   useM1 = nodes_in_bounding_box(M2,M1,th);
   useM1 = find(useM1);
   useM2 = nodes_in_bounding_box(M1,M2,th);
   
   if isempty(useM1) || all(~useM2(:))
      M1 = naive_join(M1,M2);
      continue
   end
   
   nodes_to_add = M2.nodes(~useM2,:);
   n_new_nodes = nnz(~useM2);
   match = zeros(length(M2.nodes),1);
   match(~useM2) = l1 + (1:n_new_nodes);
   useM2 = find(useM2);
   N = length(useM2');
   for j = 1:N
      if mod(j,100)==1, progress_msg(j/N); end
      n = useM2(j); 
      
      use = nodes_near_node(M1.nodes(useM1,:), M2.nodes(n,:), 1.1*th);
      switch nnz(use)
         case 0
         case 1
            match(n) = useM1(use);
         otherwise
            use = useM1(use);
            len_use = length(use);
            D = M1.nodes(use,:) - ones(len_use,1)*M2.nodes(n,:);
            D = sum(D.^2,2); % sqrt(sum(D.^2,2)); % don't need to sqrt
            [val p] = min(D);
            if val < th^2    % but then need th^2
               match(n) = use(p); % matching node of M1
            end
      end
      if ~match(n)
         match(n) = l1 + n_new_nodes+1;
         n_new_nodes = n_new_nodes + 1;
         nodes_to_add = [nodes_to_add; M2.nodes(n,:)];
      end
   end
   if do_msg, progress_msg(Inf); end
   M1.nodes = [M1.nodes; nodes_to_add];
   LE = length(M1.elems);
   for j = 1:numel(M2.mat_idx)
      M1.mat_idx{end+1} = LE+M2.mat_idx{j};
   end
   %M1.mat_idx = [M1.mat_idx {length(M1.elems)+(1:length(M2.elems))}];
   M1.elems = [M1.elems; match(M2.elems)];
   % this is not strictly correct, but visualizes nicely
   M1.boundary = [M1.boundary; match(M2.boundary)]; 
end

out =  M1;
% rmfield(M1,'boundary');

function M1 = naive_join(M1,M2)
LN = length(M1.nodes);
LE = length(M1.elems);
M1.nodes = [M1.nodes; M2.nodes];
M1.elems = [M1.elems; LN+M2.elems];
for i = 1:numel(M2.mat_idx)
   M1.mat_idx{end+1} = LE+M2.mat_idx{i};
end
M1.boundary = [M1.boundary; LN+M2.boundary];
   

function use = nodes_in_bounding_box(M2,M1,th)
   % limit to nodes in M1 that are within the bounding box of M2
   maxM2 = max(M2.nodes)+th;
   minM2 = min(M2.nodes)-th;
   use = true(length(M1.nodes),1);
   for i = 1:size(M1.nodes,2);
      use = use & M1.nodes(:,i) < maxM2(i) & M1.nodes(:,i) > minM2(i);
   end

function use = nodes_near_node(nodes,node,th)
   maxlim = node + th;
   minlim = node - th;
   use = true(size(nodes,1),1);
   for i = 1:size(nodes,2);
      use = use & nodes(:,i) < maxlim(i) & nodes(:,i) > minlim(i);
   end

function run_unit_test
subplot(221)
cyl = ng_mk_cyl_models(3,[0],[]);
show_fem(cyl)

subplot(222)
top_nodes = cyl.nodes(:,3)>=1.5;
top_elems = sum(top_nodes(cyl.elems),2)==4;
top.elems = cyl.elems(top_elems,:);
nds = unique(top.elems);
map = zeros(1,length(cyl.nodes));
map(nds) = 1:length(nds);
top.elems = map(top.elems);
top.nodes = cyl.nodes(nds,:);
top.type = 'fwd_model';
top.boundary = find_boundary(top);
show_fem(top)
zlim([0 3]);

subplot(223)
bot_elems = ~top_elems;
bot.elems = cyl.elems(bot_elems,:);
nds = unique(bot.elems);
map = zeros(1,length(cyl.nodes));
map(nds) = 1:length(nds);
bot.elems = map(bot.elems);
bot.nodes = cyl.nodes(nds,:);
bot.type = 'fwd_model';
bot.boundary = find_boundary(bot);
show_fem(bot)
zlim([0 3]);


subplot(224)
M = merge_meshes(bot, top);
show_fem(M);

unit_test_cmp('Number of nodes',length(cyl.nodes), length(M.nodes),0);
unit_test_cmp('Number of elems',length(cyl.elems), length(M.elems),0);

function img = eidors_readimg( fname, format )
% EIDORS readimg - read reconstructed image files from
%       various EIT equipment manufacturers
%  img = eidors_readimg( fname, format )
%
% Currently the list of supported file formats is:
%    - MCEIT (Goettingen / Viasys) "igt" file format 
%        format = "IGT" or "MCEIT"
%    - DIXTAL  "img" file format 
%        format = "DIXTAL-IMG"
%    - DRAEGER  "bin" file format 
%        format = "DRAEGER-BIN"
%    - NATIVE "e3d" file format
%        format = "e3d" or "NATIVE"
%
% Usage
% img = eidors_readimg( fname, format )
%     img   = eidors image structure
%     img.elem_data = reconstructed image matrix NumPixels x NumFrames
%     fname = file name
%
%  If format is unspecified, we attempt to autodetect.

% (C) 2009 by Bartlomiej Grychtol. Licensed under GPL v2 or v3
% $Id: eidors_readimg.m 6233 2022-02-15 15:05:40Z aadler $ 

if ~exist(fname,'file')
   error([fname,' does not exist']);
end

if nargin < 2
% unspecified file format, autodetect
   dotpos = find(fname == '.');
   if isempty( dotpos ) 
      error('file format unspecified, can`t autodetect');
   else
      dotpos= dotpos(end);
      format= fname( dotpos+1:end );
   end
end
fmt= lower(format);

switch fmt
    case {'igt','mceit'}
        img = mceit_readimg( fname );
    case {'dixtal-img'}
        img = read_dixtal_img( fname, 1, [] ); % Guess that FS=50
    case {'bin','draeger-bin'}
        img = read_draeger_bin( fname );
    case {'e3d','native'}
        img = native_readimg( fname );
    otherwise
        error('eidors_readdata: file "%s" format unknown', fmt);
end




%%
function img = mceit_readimg( fname )
% mceit_readimg - reads in IGT files. 

fid = fopen(fname,'r');
igt = fread(fid, inf,'4*float');
fclose(fid);

igt = reshape(igt, [], 912);

img = igt2img(igt);

img.name = ['Read from ' fname];

%%
function img = read_draeger_bin( fname );
    fid=fopen(fname,'rb');
    getarray=fread(fid, [1 inf],'int8');
    frame_length=length(getarray)/4358;
    fclose(fid);

    fmdl = mk_grid_model([],linspace(+1,-1,33),linspace(+1,-1,33));
    fmdl = rmfield(fmdl,'mdl_slice_mapper'); % set axis to match Draeger format 

    ed=zeros(1024,frame_length);     
    fid=fopen(fname,'rb');
    aux = struct([]);
    for i=1:frame_length
        time_stamp=fread(fid, [1 2],'float32');  %read time stamp
        dummy=fread(fid, [1],'float32');   %read dummy
        ed(:,i)=fread(fid, [1 1024],'float32');%read pixel values for each frame
        aux(i).int_value=fread(fid, [1 2],'int32');  %read MinMax, Event Marker,
        aux(i).EventText=fread(fid,[1 30],'int8');
        aux(i).int_Time=fread(fid, [1 ],'int32'); %Timing Error
        aux(i).Medibus=fread(fid, [1 52],'float32'); %ventilator data
        
    end
    fclose(fid);
    img = mk_image(fmdl,ed);
    img.aux = aux;

%%
function img = native_readimg( fname )
% native_readimg - reads in native E3D files.
% E3D file is a zipped matlab v6 compatible .mat file called "e3d.temp"
% containing one eidors image struct variable named "img".


if 1 % COMPATIBILITY WITH Matlab 6.5 and Octave we can't use output files
   unzip(fname);
   tempfile = 'e3d.temp';
else
   files = unzip(fname);
   if numel(files) > 1
       error(['File %s is not a proper E3D file. '...
           'The archive contains more than one file'],fname);
   end
   tempfile = files{1};
end

S = load(tempfile,'-mat');
delete(tempfile);
if numel(fieldnames(S)) > 1
     warning(['File %s is not a proper E3D file. '...
        'The mat file contains more than one variable. Strugling on.'],fname);
end

if isfield(S,'img')
    img = S.img;
else
    error(['File %s is not a proper E3D file. '...
        'The mat file does not contain an "img" variable.'],fname);
end



function [dixtalImages]=read_dixtal_img(file_name,skipHeader,Fs);
% [dixtalImages]=OpenDixtalImages(file_name,skipHeader,Fs)
%
% Read the Dixtal images at file_name
% input: 
%       - file_name:  Name and place of the dixtal file
%       - skipHeader: skip Dixtal header
%       - Fs:         sampling frequency (50 if empty)
% 
% output:
%       - dixtalImages: structure with the following fields:
%           Fs:      sampling frequency
%           datas:   analogue channel 2
%           images:  Dixtal images

if(isempty(Fs)==0)
    dixtalImages.Fs = Fs;
else
    dixtalImages.Fs = 50;
end

fid=fopen(file_name,'r','ieee-be');
[fname, mode, mformat] = fopen(fid);

%if skip header is selceted, skip the header
if (skipHeader == 1)
    for i=1:42
        tline = fgetl(fid);
    end
end
a=fread(fid,'*float32','ieee-be');
fclose(fid);

% Reshape the Images
offset = 1*32+4;
imageL = 32*32 + offset;
long = floor(length(a)/(imageL));
images = reshape(a(1:long*imageL),imageL,long);
% extracts data chanels
[dixtalImages.datas,dixtalImages.images] = ExtractDixtalDatas(images);

function [dixtalDatas,images]=ExtractDixtalDatas(images);
% [dixtalAnalogs,images]=ExtractDixtalDatas(fname)
% Extract the analog recording and the ECG from the reconstructed images of
%       - dixtalDatas structure with the following fields:
%           analog1: analogue channel 1
%           analog2: analogue channel 2
%           tbc_ecg: ECG correctness TO BE CONFIRMED
%           tbc_timeStamp: Timestamp correctness TO BE CONFIRMED
%           tbc_sync1: synchronization signal correctness TO BE CONFIRMED
%           tbc_sync2: synchronization signal correctness TO BE CONFIRMED
% !All fields starting with tbc_ are first guess signal is saved to not loos
% the data but shall be investigated!
%       - images: EIT images without the Dixtal data


% read the datas
datas=[];
imageL = size(images,2);
for i=1:36
    datas(i,:) = images(32*32+i:imageL:end,:);
end
%remove the datas form the image
images = images(1:32*32,:);

dixtalDatas.analog1 = reshape(datas(8:12,:),1,5*size(datas,2));
dixtalDatas.analog2 = reshape(datas(14:18,:),1,5*size(datas,2));
dixtalDatas.tbc_ecg = reshape(datas(20:24,:),1,5*size(datas,2));
dixtalDatas.tbc_sync1 = datas(1,:);
dixtalDatas.tbc_sync2 = datas(25,:);
dixtalDatas.tbc_timeStamp = datas(2,:);


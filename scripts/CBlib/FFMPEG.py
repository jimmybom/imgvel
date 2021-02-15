import subprocess
from datetime import datetime
import os
import re


#import local libraries
import CBlib.Log as Log

def captureIPstream(config, Cam = 1):
    
    CamNum = 'Camera{0}'.format(Cam)
    #camera address
    CameraIP = config[CamNum]['IP']
    CameraUser = config[CamNum]['User']
    CameraPwd = config[CamNum]['Pwd']
    CameraPort = config[CamNum]['RTSP_Port']
    
    #Media details specific to camera
    CameraPort = config[CamNum]['RTSP_Port']
    VideoFolder = config[CamNum]['stor_path_video']
    ImageFolder = config[CamNum]['stor_path_image']
    VideoLength = config[CamNum]['length_video_sec']
    VideoFormat = config[CamNum]['format_video']


    #station details
    StationNumber = config['DEFAULT']['Station_Number']
    ffmpegpath = config['DefaultVideoConfig']['ffmpeg_local']

    
    #fill in default values if not specific to camera
    if not VideoFolder:
        VideoFolder = config['DefaultStorage']['stor_path_video']
    if not ImageFolder:
        ImageFolder = config['DefaultStorage']['stor_path_image']
    if not VideoFormat:
        VideoFormat = config['DefaultVideoConfig']['format_video']
    if not VideoLength:
        VideoLength = config['DefaultVideoConfig']['length_video_sec']

      
    #create storage folders if they don't already exist
    if not os.path.exists(VideoFolder):
        os.makedirs(VideoFolder)
    if not os.path.exists(ImageFolder):
        os.makedirs(ImageFolder)

    TimeStamp = datetime.today().strftime('%Y%m%d_%H%M%S') #formated for re.match exact string

    #****************************************************************************
    #Record
    
    Log.printandlog("Capturing Video from {x}".format(x = CamNum))
    #define some commands and variables
    #TimeStamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    VideoName = StationNumber + "_" + TimeStamp + "_" + CamNum + "." + VideoFormat
    VideoPath = os.path.join(VideoFolder,VideoName)
    
    #camera source
    if(CameraPort.isdigit()):
        cam_source = (
                '-i rtsp://{CamUser}:{CamPwd}@{CamIP}:{CamPort} ' #camera source
                     ).format( #output filename
                        CamUser = CameraUser,
                        CamPwd = CameraPwd,
                        CamIP = CameraIP,
                        CamPort = CameraPort
                        )
    else:
        cam_source = (
                    '-i rtsp://{CamUser}:{CamPwd}@{CamIP}/{CamPort} ' #camera source
                        ).format( #output filename
                        CamUser = CameraUser,
                        CamPwd = CameraPwd,
                        CamIP = CameraIP,
                        CamPort = CameraPort
                        )

    #capture the video stream to specified format
    cmd = (
            '{ff} ' #cmd for ffmpeg
            '{cm} ' #camera source
            '-t {vtime} ' #length of video (seconds)
            '-vcodec copy -acodec copy ' #copy codecs
            '-ss 10 ' #this turns on the feed, but delays it by X seconds and reduces and initial errors from ffmpeg
            '{Ipath}').format( #output filename
                ff = ffmpegpath,
                cm = cam_source,
                vtime = VideoLength,
                Ipath = VideoPath)
                
    result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True)
                    
    Log.printandlog("Capturing IP Stream")
    Log.printandlog(cmd)
    Log.printandlog(result.stdout)

    return(VideoPath)

    
def videotoimage(inVideoPath, outImagePath, ffmpegpath = 'ffmpeg '):
    '''
    base function to extract image (2 seconds in) from a video using ffmpeg
    '''
    

    
    if not os.path.exists(outImagePath):
                        #todo add ffmpegconverttoimagefunction in the FFMPEG module
                        cmd = '{ff} -i {iv} -ss 2 -vframes 1 {oi}'.format(
                            ff = ffmpegpath,
                            iv = inVideoPath,
                            oi = outImagePath)
                        
                        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                universal_newlines=True)
                        
                        Log.printandlog("Extracting Image from video")
                        Log.printandlog(cmd)
                        Log.printandlog(result.stdout)
                        
                        
def extractimage(config, VideoPath):
    '''
    wrapping function. Given a video path, will figure out new image path and extract first image from video
    '''
    
    videoname = os.path.basename(VideoPath) #standard format is 'Station#_YYYYMMDD_HHmmss_CameraX.xxx'
    ProcessedImagePath = config['DefaultStorage']['stor_path_image']
    ffmpegpath = config['DefaultVideoConfig']['ffmpeg_local']
    
    if not os.path.exists(ProcessedImagePath):
        os.makedirs(ProcessedImagePath)
    
    # extract first image and store in images directory
    outimage = '{Stn}_{DS}T{TS}Z.jpg'.format(
        Stn = videoname.split("_")[0],
        DS = videoname.split("_")[1],
        TS = re.split('\.|_',videoname)[2])

    outimagepath = os.path.join(ProcessedImagePath, outimage)

    
    videotoimage(VideoPath, outimagepath, ffmpegpath)



    
    
    

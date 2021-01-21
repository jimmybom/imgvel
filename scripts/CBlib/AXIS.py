#library of functions to copy the contents of the SD card on an AXIS camera

import ftplib
import os
import re
import subprocess
from datetime import datetime
import logging
import shutil

#import local libraries
import CBlib.Log as Log
import CBlib.FFMPEG as FFMPEG



def _is_ftp_dir(name):
    '''
    determines if an item listed on the ftp server is a directory
    '''

    # if the length is less than 3 it is probably a directory
    if len(name) <=3:
        return True
    
    #if it has a '.' in the 3rd or 4th last position, it is a file
    if name[-4]  == '.' or name[-3] == '.':
        return False
    
    #else it is a directory
    else:
        return True
    
    

def _is_ftp_media(name):
    '''
    determines if an item listed on the ftp server a media file
    '''

    # if the length is less than 3 it is probably a directory
    if len(name) <=3:
        return False
    
    #check if it has common media file extensions
    if name[-4:]  == '.mkv' or name[-4:] == '.mp4' or name[-4:] == '.avi':
        return True
    
    #else it isn't a media file
    else:
        return False


def _download_ftp_file(ftp_handle, name, dest, overwrite):
    '''
    downloads a single file from an ftp server
    handle = open(path.rstrip("/") + "/" + filename.lstrip("/"), 'wb')
    ftp.retrbinary('RETR %s' % filename, handle.write)
    '''
    if not os.path.exists(dest) or overwrite is True:
        with open(dest, 'wb') as f:
            ftp_handle.retrbinary("RETR {0}".format(name), f.write)
        Log.printandlog("downloaded: {0}".format(dest))
    else:
        Log.printandlog("already exists: {0}".format(dest))



def _mirror_ftp_dir(ftp_handle, name, dest, overwrite, config, Cam):
    '''
    replicates a directory on an ftp server recursively
    '''
    
    for item in ftp_handle.nlst(name):
        
        #check if isn't valid name
        if item == ".." or item == ".":
            continue
        
        #check if is a directory and enter it if possible
        if _is_ftp_dir(item):
            newname = os.path.join(name,item)
            try:
                _mirror_ftp_dir(ftp_handle, newname, dest, overwrite, config, Cam)
            except:
                Log.printandlog("Could not enter FTP Directory: " + newname)
                
        #else is a valid file
        else:
            if _is_ftp_media(item):

                localpath = os.path.join(dest,formatvideoname(item, config, Cam))
                remotepath = os.path.join(name, item)
                
                if not os.path.exists(localpath):                    
                    try:
                        #download the file
                        _download_ftp_file(ftp_handle, remotepath, localpath, overwrite)
                        
                        #extract image and save
                        FFMPEG.extractimage(config, localpath)
                        
                    except:
                        Log.printandlog("Could not download file")
        



def download_ftp_tree(ftp_handle, path, destination, overwrite, config, Cam):
    '''
    Downloads an entire directory tree from an ftp server to the local destination

    :param ftp_handle: an authenticated ftplib.FTP instance
    :param path: the folder on the ftp server to download
    :param destination: the local directory to store the copied folder
    :param overwrite: set to True to force re-download of all files, even if they appear to exist already
    '''

    _mirror_ftp_dir(ftp_handle, path, destination, overwrite, config, Cam)
    



def CopySDCard(config, Cam = 1):
    '''
    copy contents of SD card on AXIS cam
    '''
    
    Log.printandlog("###################### Copy SD Card #########################")
    Log.printandlog("Copying Camera SD card to RPI")
    
    #Parse the relevant configuration details
    CamNum = 'Camera' + str(Cam)
    Log.printandlog(CamNum)
    
    #camera address
    CameraIP = config[CamNum]['IP']
    CameraUser = config[CamNum]['User']
    CameraPwd = config[CamNum]['Pwd']
    CameraFTP = config[CamNum]['FTP_dir']
    RPI_vid_storage = config['DefaultStorage']['stor_path_video']
    
    #check to make SD dump directory exists
    if not os.path.exists(RPI_vid_storage):
        os.makedirs(RPI_vid_storage)
    
    Log.printandlog("Connect to FTP" + str(CameraIP))
    ftp = ftplib.FTP(CameraIP, CameraUser, CameraPwd)
    Log.printandlog("Downloading data from SD card via ftp")
    download_ftp_tree(ftp, CameraFTP, RPI_vid_storage, False, config, Cam)
    
    
            

def formatvideoname(vidname, config, Cam):
    '''
    change AXIS video name to conform with Image Velocimetry Standards
    '''
    
    StationNumber = config['DEFAULT']['Station_Number']
    CamString = 'Camera' + str(Cam)
    
    outvideo = '{Stn}_{DS}_{TS}_{CM}.{ext}'.format(
    Stn = StationNumber,
    DS = vidname.split("_")[0],
    TS = vidname.split("_")[1],
    CM = CamString,
    ext = vidname[-3:])
    
    return(outvideo)
    

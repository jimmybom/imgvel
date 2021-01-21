
import datetime
import sys
import os
import ftplib
import configparser
import argparse
import logging


import CBlib.Log as Log


def FtpNewmedias(ftp_limit = 10, Cam = 1, Media = 'video'):
    """
    This function takes the images stored in the base storage directory (as
    defined in the configuration file), and then tries to ftp them to
    an offsite location. If the transfer is successfull, the original
    file also gets moved to a longterm storage directory for redundancy
    
    User can define the maximum number of images they want transferred,
    the default is 10
    """
        #****************************************************************************
    #get the option arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", help="integer to decide what camera to use (1-4)", type = int)
    parser.add_argument("--media", help="video or image, default is video", type = str)
    parser.add_argument("--trans_limit", help="transfer limit, integer", type = int)
    args = parser.parse_args()
    
    #If a commandline argument is given, use it to overwrite the default camera
    if args.camera:
        Cam = args.camera
    
    #If a commandline argument is given, use it to overwrite the default media type
    if args.media:
        Media = args.media
        
    #If a commandline argument is given, use it to overwrite the default transfer limit
    if args.trans_limit:
        ftp_limit = args.trans_limit
    



    #Read the configuration file
    config = configparser.ConfigParser()
    config.read('StationConfig.ini') #assumed to be in the same folder as script
    
    #Parse the relevant configuration details
    StationNumber = config['DEFAULT']['Station_Number']
    CamNum = 'Camera' + str(Cam)
    
    
    #set video path defaults if that is what is selected
    if Media == 'video':
        #First try the camera specific path
        if config[CamNum]['stor_path_video']:
            storage_path = config[CamNum]['stor_path_video']
        else:
            storage_path = config['DefaultStorage']['stor_path_video']
        
        
        #define folder where files go after they are ftp'd
        longterm_stor_path = config['DefaultStorage']['longterm_stor_path_video']
        ftp_directory = config['FTP']['Directory_Video']
        

        
        
    #set image path defaults if that is what is selected
    if Media == 'image':
        #First try the camera specific path
        if config[CamNum]['stor_path_image']:
            storage_path = config[CamNum]['stor_path_image']
        else:
            storage_path = config['DefaultStorage']['stor_path_image']
        
        #define folder where files go after they are ftp'd
        longterm_stor_path = config['DefaultStorage']['longterm_stor_path_image']
        ftp_directory = config['FTP']['Directory_Image']
        
        
        
    if not os.path.exists(longterm_stor_path):
        os.makedirs(longterm_stor_path)
    
    
    
    
    #set ftp defaults
    ftp_address = config['FTP']['Address']
    ftp_user = config['FTP']['User']
    ftp_pwd = config['FTP']['Pwd']
    ftp_maxtime = int(config['FTP']['Timeout_Video'])



    #search the directory and get a list of just the videos
    list_of_files = os.listdir(storage_path)
    list_of_media = [os.path.join(storage_path,i) for i in list_of_files if (i.endswith(('.mp4', '.mkv', 'jpg', 'jpeg')))]
    list_of_media = sorted(list_of_media)[::-1] #reorder so the newest video is first




    ftp_limit = min(ftp_limit,len(list_of_media)) #ensure the user defined number isn't bigger than the number of video files

    #print message if no videos will be uploaded
    if ftp_limit == 0:
        Log.printandlog("No media to upload")
        
    #subset to a maximum of the limit set by the user at the beginning of the script 
    ftp_list = list_of_media[0:ftp_limit]

    #loop through the videos
    for media in ftp_list:
        media_name = os.path.basename(media)
        
        #first check if file exists in the ftp'd folder, if it does then skip the transfer and delete the orginal
        if os.path.exists(os.path.join(longterm_stor_path, media_name)):
            os.remove(media)
            Log.printandlog("File {0} has already been ftpd".format(media))
        
        else:
            try:
                Log.printandlog("Opening ftp session\n")
                session = ftplib.FTP(ftp_address, ftp_user, ftp_pwd, timeout = ftp_maxtime) 
                session.cwd(ftp_directory)
                file = open(media, 'rb')
                Log.printandlog( "Sending File: " + media_name)
                session.storbinary('STOR ' + media_name, file)
                file.close()
                Log.printandlog("file sent to ftp")
                
                #move the file
                os.rename(media,os.path.join(longterm_stor_path, media_name))
                
                Log.printandlog("Successful: File sent, local file has been moved to folder 'ftpd_vidoes'")
                session.quit()
            except Exception as e:
                Log.printandlog(str(e))
                Log.printandlog("an error occured for file: " + os.path.basename(media))
            
        
        
        
        
#execute the function if the script is being explicitly called (and not imported as a module into other code)
if __name__ == "__main__":

    #****************************************************************************
    #set logging file        
    Log.initiatelog("FTPMedialog")
    
    FtpNewmedias()

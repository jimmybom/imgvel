#script to capture an Video from a camera feed and save it with a timestamp'd name

import os
import datetime
import logging
import time
import argparse
import RPi.GPIO as GPIO

#import local libraries
import CBlib.POEcommands as POEcommands
import CBlib.AXIS as AXIS
import CBlib.Log as Log
import CBlib.FFMPEG as FFMPEG


    
#execute the function if the script is being explicitly called (and not imported as a module into other code)
if __name__ == "__main__":


    #****************************************************************************
    Log.initiatelog("GrabMedia")
    
    #get the option arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", help="integer to decide what camera to use (1-4)", type = int)
    args = parser.parse_args()
    
    #If camera is specified, use that. otherwise default to camera 1
    if args.camera:
        Cam = args.camera
    else:
        Cam = 1
    
    CamString = 'Camera' + str(Cam)
    
    Log.printandlog("Grab Media from Camera {0}".format(Cam))
    
    
    
    #run functions
    c = POEcommands.importconfig('StationConfig.ini')
    POEcommands.TurnPOEon(c)
    POEcommands.WarmupPOE(c)
    
    
    
    #check camera type
    CameraSD = c.getboolean(CamString,'SD_storage')

    
    if CameraSD == True:
        Log.printandlog("Grabbing media from SD card")
        
        timepause = 30
        Log.printandlog("Waiting {0} seconds for Camera to record to SD card and establish FTP connection".format(timepause))
        time.sleep(timepause) #camera must be on for at least 30 seconds for ftp connection to be established
        
        AXIS.CopySDCard(config = c, Cam = Cam)
        POEcommands.TurnPOEoff(c)
        Log.printandlog("Axis capture and process ran successfully")
        
        
    #else grab media from IP stream    
    else:
        Log.printandlog("Grabbing media from IP Stream")
        
        vidpath = FFMPEG.captureIPstream(config = c, Cam = Cam) #captures and saves video
        FFMPEG.extractimage(config = c, VideoPath = vidpath) #extract image from video that was just recorded
        POEcommands.TurnPOEoff(c)
        
        Log.printandlog("video successfully captured from IP stream")
        
        

    ##capture IP stream via ffmpeg
    
    Log.printandlog("Camera capture and process ran successfully")
    



    


#This script continously checks the input from the FTS logger (via the GPIO pins)
#if it receives a signal, it triggers a shell script to record a video

import RPi.GPIO as GPIO
import datetime
import time
import subprocess
import GrabMedia
import configparser

# Setup the GPIOs
# Set pin and listen
PortNumber = 7 #where the FTS is connected to the GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PortNumber, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(PortNumber, GPIO.BOTH)



# Sub to watch pin 
# If pin is set high, run the record script every dT minutes until pin is set low again

def CheckSensorTriggerCam():

    #Read the configuration file
    config = configparser.ConfigParser()
    config.read('StationConfig.ini') #assumed to be in the same folder as script
    

    
    #camera toggles
    Camera1 = bool(config['Camera1']['highwater_retrieval'])
    Camera2 = bool(config['Camera2']['highwater_retrieval'])
    Camera3 = bool(config['Camera3']['highwater_retrieval'])
    Camera4 = bool(config['Camera4']['highwater_retrieval'])
    
    highwater_interval = int(config['DefaultVideoConfig']['highwater_interval'])
    highwater_sundown = int(config['DefaultVideoConfig']['highwater_sundown'])
    
    
    #Set the frequency tha the PI checks for input in seconds
    HWI = highwater_interval * 60 #minutes * seconds
    timestep = 15 #check every 15 seconds
    
    counter = 0
    while True:
        counter = counter + timestep
        i = GPIO.input(PortNumber)
        currenttime = datetime.datetime.now().time()
        closetime = currenttime.replace(hour=highwater_sundown, minute=0, second=0, microsecond=0)
        
        #shut down if nighttime (currently set for 9pm)
        if currenttime > closetime:
            exit()
            
            
        else:
            #case 1: low water
            if i == 0:
                time.sleep(timestep)
                print('Port is Off. ' + str(counter) + 's elasped')
                
            #case 2: high water
            else:
                time.sleep(timestep)
                if counter > HWI: #make sure the command hasn't been run in the last few seconds (dT)
                    counter = 0
                    print ('Port is turned on, script running ' + str(counter))
                    
                    #Turn on Cameras and wait for internal clocks to be set
                    GrabMedia.TurnPOEon()
                    GrabMedia.WarmupPOE()
                    
                    #record image and video from any camera that has the 'highwater_retrieval' flag turn on in the .ini file
                    if(Camera1):
                        GrabMedia.GrabMedia(Cam = 1, Media = 'image')
                        GrabMedia.GrabMedia(Cam = 1, Media = 'video')
                    if(Camera2):
                        GrabMedia.GrabMedia(Cam = 2, Media = 'image')
                        GrabMedia.GrabMedia(Cam = 2, Media = 'video')
                    if(Camera3):
                        GrabMedia.GrabMedia(Cam = 3, Media = 'image')
                        GrabMedia.GrabMedia(Cam = 3, Media = 'video')
                    if(Camera4):
                        GrabMedia.GrabMedia(Cam = 4, Media = 'image')
                        GrabMedia.GrabMedia(Cam = 4, Media = 'video')
                        
                    GrabMedia.TurnPOEoff()
                        
                        
     
#execute the function if the script is being explicitly called (and not imported as a module into other code)
if __name__ == "__main__":
    CheckSensorTriggerCam()

    #Close all the ports
    GPIO.cleanup()


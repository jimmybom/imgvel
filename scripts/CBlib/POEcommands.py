import os
import RPi.GPIO as GPIO
import configparser
import time

#import local library
import CBlib.Log as Log



def importconfig(configpath = 'StationConfig.ini'):
    
    Log.printandlog("Reading configuration file: {0}".format(configpath))
    
    #Read the configuration file
    config = configparser.ConfigParser()
    config.read(configpath) #assumed to be in the same folder as script
    
    Log.printandlog("Configuration file successfully read")
    
    return(config)
    
    
    

 

def TurnPOEon(config):
    '''
    Function to turn the POE router on, this will power up all of the IP cameras
    '''
    #get pin number from config file
    PowerPin = int(config['GPIO']['POE']) 
    Log.printandlog("Turning POE on (via Pin {0})".format(PowerPin))
    
    

    GPIO.setmode(GPIO.BOARD) # set GPI mode
    GPIO.setup(PowerPin,GPIO.OUT) #configure pin to output
    GPIO.output(PowerPin,GPIO.LOW)#turn pin voltage to low, this will turn POE on (as per relay design)
    
    Log.printandlog("PIN {0} is turned on".format(PowerPin))

    
    

def WarmupPOE(config):
    '''
    Function to wait for the POE to power up, doing so will allow the cameras to
    set their internal clocks. The ActiA31 cameras queries the NRC online clock
    every 5 minutes
    '''
    
    
    
    WarmUp = int(config['DefaultVideoConfig']['warmup'])
    
    Log.printandlog("Waiting {x} seconds for camera system to turn on and set clock".format(x = WarmUp))

    time.sleep(WarmUp)  
    
    
    
def TurnPOEoff(config):
    '''
    Function to turn the POE router off, this will power down all of the IP cameras
    '''

    PowerPin = int(config['GPIO']['POE'])
    
    Log.printandlog("Turning POE off (via Pin {0})".format(PowerPin))
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) # set GPI mode
    GPIO.setup(PowerPin,GPIO.OUT) #configure pin 11 to output
    GPIO.output(PowerPin,GPIO.HIGH)
    GPIO.cleanup()
    
    Log.printandlog("PIN {0} is turned off".format(PowerPin))
 
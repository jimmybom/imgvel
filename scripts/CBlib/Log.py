import logging
import os
import datetime
import sys


        
        
def printandlog(statement):
    #print(statement)
    logging.info(statement)


def initiatelog(logname):
        #set logging file
    if not os.path.exists("Logs"):
        os.makedirs("Logs") 
    
    TimeStamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    LogName = os.path.join("Logs", TimeStamp + '_{0}.txt'.format(logname))
    
    #https://stackoverflow.com/questions/9321741/printing-to-screen-and-writing-to-a-file-at-the-same-time
    level    = logging.DEBUG
    format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers = [logging.FileHandler(LogName), logging.StreamHandler(sys.stdout)]

    logging.basicConfig(level = level, format = format, handlers = handlers)


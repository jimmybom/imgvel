#Script to check free space on SD Card and delete files if disk is getting full
# set this to run once a day in crontab

#import necessary python libraries
import shutil
from pathlib import Path
import os
import logging
import datetime



#set some user inputs
#Set deleting threshold (start deleting files if less than this much available space (GB))
delete_threshold = 2

#Set resting thrshold (stop deleting files after this much space is free (GB))
space_required = 10

#delete files from these folders in this order until the space_required is reached
priority_folders = ['/home/pi/lspiv/video_ops/ftpd_videos/',
                    '/home/pi/lspiv/image_ops/ftpd_images/']



#define supporting functions
def deleteandcheck(folder, space_required):
        #calculated free space
        total, used, free = shutil.disk_usage("/")
        free_gb = free/(2**30)
        

        
        while free_gb < space_required:
            
            #get list of files (not folders) in main folder
            listoffiles = [os.path.join(folder,name) for name in os.listdir(folder) if os.path.isfile(os.path.join(folder,name))]

            
            #if there are no files, then exit function
            if len(listoffiles) == 0:
                #print("still not enough space, but there are no more files to delete")
                break
        
            #delete 10 oldest files
            #print("deleting 10 files from: ", folder)
            filestodelete = listoffiles[0:10]
            #print("Deleting files: ", filestodelete)
            for f in filestodelete:
                os.remove(f)
                
            #calculated free space in order to loop back if necessary
            total, used, free = shutil.disk_usage("/")
            free_gb = free/(2**30)
        
    
    
#function to get the size of a directory
def get_dir_size(DirectoryPath):
        root_directory = Path(DirectoryPath)
        size_gb = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())/(2**30)
        return(size_gb)
        


######MAIN SCRIPT#####################################
#execute the function if the script is being explicitly called (and not imported as a module into other code)
if __name__ == "__main__":

    #****************************************************************************
    #set logging file
    if not os.path.exists("Logs"):
        os.makedirs("Logs") 
    
    TimeStamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    LogName = os.path.join("Logs", TimeStamp + '_CheckPiHDspace.txt')
    logging.basicConfig(filename = LogName, level=logging.INFO)
    logging.captureWarnings(True)

    #get capacity of SD Card, we should be using a minimum size of 128GB cards
    total, used, free = shutil.disk_usage("/")
    total_gb = total/(2**30)
    used_gb = used/(2**30)
    free_gb = free/(2**30)



    #check resting threshold is larger than deleting threshold
    if space_required < delete_threshold:
        space_required = delete_threshold + 1


    #if free space is under a threshold then:
    if free_gb < delete_threshold:
        logging.info("Available space on hard disk:" + "{:.2f} GB".format(free_gb))
        logging.info("Threshold to start clearing hard disk (GB):"+ "{:.2f}".format(delete_threshold))
        logging.info("Deleting files until "+ "{:.2f} GB".format(space_required), "is available or all folders are cleared")
        logging.info("Deleting from folders in the following priority: " + str(priority_folders))
        
        #loop through each folder
        for fold in priority_folders:
        
            #calculate free space
            total, used, free = shutil.disk_usage("/")
            free_gb = free/(2**30)
            
            #print("free space: ", "{:.2f}".format(free_gb))
            #print("space required:", "{:.2f}".format(space_required))
            
            if free_gb < space_required:

                #get size of folder
                fold_size = get_dir_size(fold)
                
                #if folder contents is less than required space then just delete everything in the folder
                if (fold_size + free_gb) < space_required:
                    logging.info(fold + ":Deleting everything here.")

                    
                    #get list of files (not folders) in main folder
                    listoffiles = [os.path.join(fold,name) for name in os.listdir(fold) if os.path.isfile(os.path.join(fold,name))]
           
                    for f in listoffiles:
                        os.remove(f)
                        
                        
                #else go into the folder and delete 10 files at a time until capacity is reached or there are no more files
                else:
                    logging.info(fold + ":Deleting some files until space requirements met.")
                    deleteandcheck(fold, space_required)
                   
            else:
                #Success, space requirements met, lets end script
                break
                    
                    
        #get capacity again and return final message
        total, used, free = shutil.disk_usage("/")
        total_gb = total/(2**30)
        used_gb = used/(2**30)
        free_gb = free/(2**30)
        logging.info("\n\nClearing specificied folders is complete")
        logging.info("Available space on hard disk:"+ "{:.2f} GB".format(free_gb))
        if(space_required < free_gb):
            logging.info("Space required: {:.2f} GB".format(space_required))
        else:
            logging.info("Space required: {:.2f} GB,".format(space_required) + " but there are no more available files to delete")
        
                
    else:
        logging.info("Available space on hard disk:"+ "{:.2f}".format(free_gb))
        logging.info("Threshold to start clearing hard disk (GB):"+ "{:.2f}".format(delete_threshold))
        logging.info("Not deleting files today:)")
        


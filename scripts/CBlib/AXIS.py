#library of functions to control AXIS camera
import requests
import shutil
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree


import os




class CAM:
    def __init__(self, host, username, password):
        '''
        Initialize axiscam object
        
        :param host (str): the camera's ip address or host name
        :param username (str): camera username
        :param password (str): camaera password
        '''
        self.host = host
        self.username = username
        self.password = password
        
        
    def user_or_password_error(self):
        print('[-] Username or password error')


    def error_with_status_code(self):
        print('[-] Error: ' + str(r.status_code))
        
        
    def getvideolist(self):
        'get list of recordings'
        response = requests.get("http://{}/axis-cgi/record/list.cgi?recordingid=all".format(self.host),
                                auth=HTTPDigestAuth(self.username, self.password))
        #use xml tree to break down xml response
        root = ElementTree.fromstring(response.content)
        
        listofvideos = []
        for child in root.iter('recording'):
            listofvideos.append(child.attrib['recordingid'])
        return(listofvideos)
    
    
    def downloadvideo(self, videoid, config):
        'download video based on recording id'

        r = requests.get('http://{}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={}&diskid=SD_DISK&exportformat=matroska'.format(self.host, videoid),
                     stream=True,auth=HTTPDigestAuth(self.username, self.password))

        outvideo = '{Stn}_{DS}_{TS}.mkv'.format(
        Stn = config['DEFAULT']['Station_Number'],
        DS = videoid.split("_")[0],
        TS = videoid.split("_")[1])
        
        outvideopath = os.path.join(config['DefaultStorage']['stor_path_video'], outvideo)
        
        
        with open(outvideopath, 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)

        
        if r.status_code == 200:
            print('[+] {} has been successfully downloaded from the AXIS SD card'.format(videoid))
        elif r.status_code == 401:
            self.user_or_password_error()
        else:
            self.error_with_status_code()
        
        del r
        
        return(outvideopath)
    
        
    def deletevideofromSDcard(self, videoid):
        'delete video on sd card by videoid'
        r = requests.get('http://{}/axis-cgi/record/remove.cgi?recordingid={}'.format(self.host, videoid),
                         auth=HTTPDigestAuth('root', 'Innovation2020'))
        
        if r.status_code == 200:
            print('[+] {} has been successfully deleted from the AXIS SD card'.format(videoid))
        elif r.status_code == 401:
            self.user_or_password_error()
        else:
            self.error_with_status_code()






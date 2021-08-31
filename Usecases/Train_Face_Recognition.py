import glob
import os
import sys
import time
from Config import config
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType
#import re
import requests
import http.client, urllib.request
'''Prerequisites: Install Face SDK: pip install azure-cognitiveservices-vision-face'''
def train(name):
    try:
        face_api_url = config.FACE_ENDPOINT + '/face/v1.0/persongroups/'+ config.PERSON_GROUP_ID+'/persons'
        face_client = FaceClient(config.FACE_ENDPOINT, CognitiveServicesCredentials(config.KEY))
        print('New student will be enrolled in Person group:', config.PERSON_GROUP_ID)
        if os.path.exists(name):    
            images = []
            [images.extend(glob.glob(name+'\*.' + e)) for e in config.FORMATS] #Reading all image formats    
    #       Check if student has been enrolled already, else delete previous enteries and train with new images
            headers = {'Ocp-Apim-Subscription-Key': config.KEY}
            params = {'detectionModel': config.DETECTION_MODEL,
                      'returnFaceId': 'true'}
    #       Get list of enrolled students to perform check        
            response = requests.get(face_api_url, params=params,
                                     headers=headers)
            resonse_name = response.json()
            for i in resonse_name:    
                if i['name'] == name:
                    delete(name)
                    print("Already enrolled student deleted, new training beings !")               
            student = face_client.person_group_person.create(config.PERSON_GROUP_ID, name)        
            for image in images:
                o = open(image, 'r+b')
                face_client.person_group_person.add_face_from_stream(config.PERSON_GROUP_ID, student.person_id, o)
            
            face_client.person_group.train(config.PERSON_GROUP_ID)
            while (True):
                training_status = face_client.person_group.get_training_status(config.PERSON_GROUP_ID)
                print("Training status: {}.".format(training_status.status))                
                if (training_status.status is TrainingStatusType.succeeded):
                    break
                elif (training_status.status is TrainingStatusType.failed):
                    sys.exit('Training the person group has failed.')
                time.sleep(1)
        else:
            print("Image folder not found")
    except:
        print("Images not found in the current directory or recheck the format of image name")
        
#     This delete funtion is taking the parameter name for deleting the name in the train loop
def delete(name):        
    headers = {'Ocp-Apim-Subscription-Key': config.KEY}
    student_name = name    
    face_api_url = config.FACE_ENDPOINT + '/face/v1.0/persongroups/'+config.PERSON_GROUP_ID+'/persons'    
    response = requests.get(face_api_url,headers=headers)
    responsefile = response.json()
    
    def get_id(responsefile, student_name):
        for i in responsefile:
            if i.get('name') == student_name:
                studentid = i.get('personId')
                return studentid
            else: 
                continue
    Student_Id = get_id(responsefile, student_name)
    if Student_Id is None:
        print("Student not found in this group")
    else:    
        try:
            sid = "/face/v1.0/persongroups/"+config.PERSON_GROUP_ID+"/persons/"+Student_Id+"?%s" 
            conn = http.client.HTTPSConnection('southeastasia.api.cognitive.microsoft.com')
            conn.request("DELETE", sid ,"{body}", headers)
            response = conn.getresponse()
            print('{} has been deleted from the group name : {}.'.format(student_name, config.PERSON_GROUP_ID))
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
                
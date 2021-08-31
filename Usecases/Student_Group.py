from Config import config
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import json, requests

def create_group():        
    try:    
        face_client = FaceClient(config.FACE_ENDPOINT, CognitiveServicesCredentials(config.KEY))
        print('Person group name:', config.PERSON_GROUP_ID)
        #Person Group Created
        face_client.person_group.create(person_group_id= config.PERSON_GROUP_ID, name= config.PERSON_GROUP_ID)
        print('Created person group:', config.PERSON_GROUP_ID)
    except:
        print("Group already present, Try another name that must confirm to the following pattern: '^[a-z0-9-_]+$'")

def delete_group():    
    face_client = FaceClient(config.FACE_ENDPOINT, CognitiveServicesCredentils(config.KEY))
    print('DELETING PERSON GROUP')
    # Delete the person group.        
    try:
        if config.PERSON_GROUP_ID is None:
            print("Person Group is not found")
        else:
            face_client.person_group.delete(person_group_id = config.PERSON_GROUP_ID)
            print("Deleted the person group {} from the source location.".format(config.PERSON_GROUP_ID))
    except:
        print("Person group doesnt exist")        

def student_list():
    try:        
        face_api_url = config.FACE_ENDPOINT + '/face/v1.0/persongroups/'+ config.PERSON_GROUP_ID +'/persons'
        
        headers = {'Ocp-Apim-Subscription-Key': config.KEY}
        params = {
        	'detectionModel': config.DETECTION_MODEL,
            'returnFaceId': 'true'
        }
        
        response = requests.get(face_api_url, params=params,
                                 headers=headers)
        
        print(response.json())
        
    except:
        print("List not found")
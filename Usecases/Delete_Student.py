from Config import config
import http.client, urllib.request
import requests

def delete_student(name):        
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

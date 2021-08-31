import glob
import os
import time
import cv2
from PIL import Image, ImageDraw
from Config import config
# To install this module, run:
# python -m pip install Pillowfrom azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face import FaceClient
''' Prerequisites: Install Face SDK: pip install azure-cognitiveservices-vision-face '''
def test():    
    # Create an authenticated FaceClient.
    face_client = FaceClient(config.FACE_ENDPOINT, CognitiveServicesCredentials(config.KEY))
    #Declaring varibles
    writer= None
    height= None
    width= None
    totalFrames = 0
    
    date_time_string = time.strftime(config.DATE_TIME_FORMAT)
    
    vs = cv2.VideoCapture(config.URL)
    
    def getRectangle(faceDictionary):
        rect = faceDictionary.face_rectangle
        left = rect.left
        top = rect.top
        right = left + rect.width
        bottom = top + rect.height
        return ((left-30, top-50), (right+30, bottom+50))
    
    while(True):
        ret, frame = vs.read()
        if frame is None:
            print("frame not found")
            break
        if width is None or height is None:
            (height, width) = frame.shape[:2]
        
        if totalFrames % 5 == 0:
            print("Detection under process")
            imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(imageRGB)
            im.save('temp.jpg')
            image = open('temp.jpg', 'r+b')
            test_image = Image.open('temp.jpg')
            print("Image saved and uploaded")
            face_ids = []
    
            faces = face_client.face.detect_with_stream(image, config.DETECTION_MODEL)
            for face in faces:
                face_ids.append(face.face_id)
                print("The detected face id is :",face.face_id)
                (left,top),(right,bottom)= getRectangle(face)
                cv2.rectangle(frame,(left,top),(right,bottom), (0, 0, 255), 2)
                results = face_client.face.identify(face_ids, config.PERSON_GROUP_ID)
                print('Identifying faces in {}'.format(os.path.basename(image.name)))
                if not results:
                    print('No person identified in the person group for faces from {}.'.format(os.path.basename(image.name)))
                    
                for person in results:
                    if len(person.candidates) > 0 :
                              if (person.candidates[0].confidence) > config.CONFIDENCE_THRESHOLD :
                                  
                                  print('Person for face ID {} is identified in {} with a confidence of {}.'.format(person.face_id, os.path.basename(image.name), person.candidates[0].confidence)) # Get topmost confidence score
                                  person_id = person.candidates[0].person_id
                                  results = face_client.person_group_person.get(config.PERSON_GROUP_ID, person_id)
                                  person_details = eval(str(results))
                                  #Appending date and time stamp with detected image saved in directory                           
#                                  name_date= person_details['name']+ date_string
                                  name_date_time = person_details['name']+ date_time_string+'.png'
                                  print('Drawing rectangle around face... see popup for results.')
                                  (left,top),(right,bottom)= getRectangle(face)
                                  name_split1, name_split2 = name_date_time.split("Time")
                                  files=glob.glob(name_split1+"*.png")                                 
                                  
                                  if len(files) >= 1:                                                                   
                                      print("Attandance has been marked. Image already present in the directory.")
                                      cv2.rectangle(frame,(left,top),(right,bottom), (255,0,0), 2)
                                      cv2.putText(frame, str(person_details['name']+" already marked for today"), (left,top-40), 1, 2, (255,255,255), 2)                                                                                                                
                                      cv2.imshow("Face Recognition", frame)
                                      
                                  else:
                                      print("Recognized Student Name: ",person_details['name'])
                                      cv2.rectangle(frame,(left,top),(right,bottom), (0, 255, 0), 2)
                                      cv2.putText(frame, str(person_details['name']), (left,top-40), 1, 2, (255,255,255), 2)
                                      cv2.imshow("Face Recognition", frame)
                                      draw = ImageDraw.Draw(test_image)
                                      draw.rectangle(getRectangle(face), outline='green')
                                      crop_image = test_image.crop((left,top, right, bottom))
                                      crop_image.save(name_date_time)
                                      print("Image saved after detection")                                                    

                    else:
                        print('No person identified for face ID {} in {}.'.format(person.face_id, os.path.basename(image.name)))
                                                
            if writer is not None:
                 writer.write(frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        totalFrames += 1
          
    if writer is not None:
        writer.release()
    vs.release()
    cv2.destroyAllWindows()

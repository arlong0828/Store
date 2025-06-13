# from django.test import TestCase
# from azure
# Create your tests here.
from azures import key_point
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
Key , Point  = key_point()
PERSON_GROUP_ID = 'school_face_identification'
face_client = FaceClient(Point , CognitiveServicesCredentials(Key))
face_client.person_group.create(PERSON_GROUP_ID , name= "name")
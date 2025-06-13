from store_app.azures import key_point
import time
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face import FaceClient
from .models import faceID
from store_app.upload_img import Upload_image
def faceGroup(name = None , img1 = None , img2 = None , img3 = None):
    Key , Point  = key_point()
    face_client = FaceClient(Point , CognitiveServicesCredentials(Key))
    PERSON_GROUP_ID = 'school_face_identification'
    
    img1_data = Upload_image(img1)
    print(img1_data)

    if len(img2) > 0:
        img2_data = Upload_image(img2)
        print(img2_data)
        Keys = face_client.person_group_person.create(PERSON_GROUP_ID , name)
        Key_image = [img1_data , img2_data]

    if len(img3) > 0:
        img3_data = Upload_image(img3)
        print(img3_data)
        Keys = face_client.person_group_person.create(PERSON_GROUP_ID , name)
        Key_image = [img1_data , img2_data , img3_data]
    people = faceID.objects.get(faceID_name = name)
    people.faceID_number = Keys.person_id
    people.save()
    for image in Key_image:
        face_client.person_group_person.add_face_from_url(PERSON_GROUP_ID , Keys.person_id , image)
    print("開始訓練!")
    face_client.person_group.train(PERSON_GROUP_ID)
    while True:
        training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
        if (training_status.status is TrainingStatusType.succeeded):
            print("訓練完成!")
            break
        elif (training_status.status is TrainingStatusType.failed):
            print("訓練錯誤!")
            break
        time.sleep(5)
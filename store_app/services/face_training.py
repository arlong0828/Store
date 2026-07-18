import time

from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from msrest.authentication import CognitiveServicesCredentials

from store_app.models import faceID

from .azure_config import azure_face_credentials
from .image_upload import upload_image


PERSON_GROUP_ID = "school_face_identification"


def train_member_face(account):
    """Add a member's three profile photos to the Azure person group."""
    key, endpoint = azure_face_credentials()
    client = FaceClient(endpoint, CognitiveServicesCredentials(key))
    image_urls = [upload_image(photo.path) for photo in (account.cPhoto1, account.cPhoto2, account.cPhoto3)]
    person = client.person_group_person.create(PERSON_GROUP_ID, account.cName)

    profile = faceID.objects.get(faceID_name=account.cName)
    profile.faceID_number = person.person_id
    profile.save(update_fields=["faceID_number"])

    for image_url in image_urls:
        client.person_group_person.add_face_from_url(PERSON_GROUP_ID, person.person_id, image_url)

    client.person_group.train(PERSON_GROUP_ID)
    while True:
        status = client.person_group.get_training_status(PERSON_GROUP_ID)
        if status.status is TrainingStatusType.succeeded:
            return
        if status.status is TrainingStatusType.failed:
            raise RuntimeError("Azure face training failed")
        time.sleep(2)

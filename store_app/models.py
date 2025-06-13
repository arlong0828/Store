from email.policy import default
from django.db import models
class member(models.Model):
    cName = models.CharField(max_length=4 , null=False)
    cSex = models.CharField(max_length=1, null=False)
    cEmail = models.EmailField(max_length=100, null=False)
    cPassward = models.CharField(max_length=20, null=False)
    cPhoto1 = models.ImageField(upload_to = "static\\media\\faceID_image", blank = False, null = False, default="")
    cPhoto2 = models.ImageField(upload_to = "static\\media\\faceID_image",null = False, blank = False , default = 'NULL')
    cPhoto3 = models.ImageField(upload_to = "static\\media\\faceID_image", null = False , blank = False , default = 'NULL')
  
    def __str__(self):
        return self.cName

class commodity(models.Model):
    commodity_Name = models.CharField(max_length=20 , null=False)
    commodity_price = models.CharField(max_length=10, null=False)
    commodity_image = models.ImageField(upload_to = "static\\media\\commodity_image", blank = False, null = False, default="")

    def __str__(self):
        return self.commodity_Name


class faceID(models.Model):
    faceID_name = models.CharField(max_length=20 , null=False, default="")
    faceID_number = models.CharField(max_length=100 , null=False, default="")
    
    def __str__(self):
        return self.faceID_name
# Create your models here.
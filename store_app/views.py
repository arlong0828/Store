from django.shortcuts import render
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import cv2,numpy
from django.http import HttpResponseRedirect, Http404,StreamingHttpResponse
from django.views import View
from store.settings import BASE_DIR
from .models import member,commodity,faceID
from store_app.camera import VideoCamera,VideoCamera2
# from keras._tf_keras.keras.models import load_model
from tensorflow.keras.models import load_model
from store_app.upload_img import Upload_image
from store_app.azures import key_point
from store_app.train_face import faceGroup
commoditylist = commodity.objects.all()
memberlist=member.objects.all()
t = '樺駿'
commodity_name = []
commodity_price = []
logout = "logout"
# 父網頁
def base(request):
    return render(request , "base.html" , locals())


# 首頁
class index(View):
    def get(self , request):
        context = {'commoditylist' : commoditylist}
        return render(request , "index.html" , context)
    def post(self , request):
        pass

# 註冊
class register(View):
    def get(self,request):
        return render(request,'register.html' ,locals())
    def post(self,request):
        allowedname=['jpg','png']
        cName=request.POST.get('cName','')
        cSex = request.POST.get('cSex','')
        cEmail = request.POST.get('cEmail','')
        cPassward = request.POST.get('cPassward','')
        cPhoto1=request.FILES.get('cPhoto1','')
        cPhoto2=request.FILES.get('cPhoto2','')
        cPhoto3=request.FILES.get('cPhoto3','')
        extenedname1=cPhoto1.name[cPhoto1.name.rindex('.')+1:]
        if extenedname1 not in  allowedname:
            return Http404()
        if len(cPhoto2) > 0:
            extenedname2=cPhoto2.name[cPhoto2.name.rindex('.')+1:]
            if extenedname2 not in allowedname:
                return Http404()
        if len(cPhoto3) > 0:
            extenedname3=cPhoto3.name[cPhoto3.name.rindex('.')+1:]
            if extenedname3 not in allowedname:
                return Http404()
        face_image = faceID.objects.create(faceID_name = cName)
        face_image.save()
        stu=member.objects.create(cName=cName,cSex = cSex,cEmail = cEmail\
            ,cPassward = cPassward,cPhoto1=cPhoto1,cPhoto2 = cPhoto2 , cPhoto3 = cPhoto3)
        member_get = member.objects.get(cName = cName)
        faceGroup(str(member_get.cName) , str(member_get.cPhoto1),str(member_get.cPhoto2)\
             , str(member_get.cPhoto3))
        if stu:
            return render(request,'index.html',locals())
        else:
            return HttpResponseRedirect('register.html')

# 登入
class login(View):
    def get(self,request):
        return render(request,'login.html' ,locals())
    def post(self,request):
        global t
        data = Upload_image(title="人員" , path="static/media/faceID_image/下載_63WyWTl.jpg")
        
        # data = Upload_image(title="人員" , path="static/face/tem.jpg")
        print(data)
        KEY , ENDPOINT  = key_point()
        face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY)) 
        PERSON_GROUP_ID = 'school_face_identification'
        faceID_all = faceID.objects.all() 
        face_ids = [] 
        test_face_image = data
        detected_faces = face_client.face.detect_with_url(url=test_face_image)
        for face in detected_faces:
            face_ids.append(face.face_id)
        results = face_client.face.identify(face_ids, PERSON_GROUP_ID)  
        personNum = 0  
        r = True
        try:
            for i, person in enumerate(results):
                if len(person.candidates) != 0: 
                    for persondict in faceID_all:
                        if str(persondict.faceID_number) == str(person.candidates[0].person_id):
                            n = faceID.objects.get(faceID_number = persondict.faceID_number)
                            r = True
                            t = n.faceID_name
                            personNum += 1
                if personNum == 0:
                    r = False
                    t = '登入失敗！你不是會員！請註冊！'
        except:
            r = False
            t = '登入失敗！！你不是會員！請註冊！'
        finally:
            
            if r:
                context = {'t':t,'commoditylist' : commoditylist}
                return render(request,'login_success_index.html',context)
            else:
                context = {'t':t}
                return render(request,'register.html',context)

def video_face(request):
    return StreamingHttpResponse(gen(VideoCamera()),content_type=\
        'multipart/x-mixed-replace; boundary=frame')

def gen(camera):
    while True:
        frame= camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# 登入成功首頁
class login_success_index(View):
    def get(self,request):
        global t
        context = {'commoditylist' : commoditylist , 't' : t}
        return render(request , "login_success_index.html" , context)
    def post(self , request):
        global t
        if logout in request.POST:
            t = ""
            context = {'commoditylist' : commoditylist , 't' : t}
            return render(request , "index.html" , context)

# 購物
class shopping(View):
    def get(self,request):
        global t
        context = {'t' : t}
        return render(request,'shopping.html' ,context)
    def post(self,request):
        global t
        if logout in request.POST:
            t = ""
            context = {'commoditylist' : commoditylist , 't' : t}
            return render(request , "index.html" , context)
        else:
            imgname = 'static/camera/tem.jpg'
            img = cv2.imread(imgname)
            gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
            test_feature = []
            size = (100,100)
            resize = cv2.resize(gray , dsize=size)
            test_feature.append(resize)
            test_feature_numpy = numpy.array(test_feature)
            test_feature_normalize = test_feature_numpy.reshape(len(test_feature_numpy)\
                ,100,100,1).astype('float32')/255
            model = load_model('static/model/shoes_CNN_Model_0.84.h5')
            prediction = model.predict(test_feature_normalize)
            prediction = numpy.argmax(prediction,axis=-1)
            m = prediction
            for commodity in commoditylist:
                if str(commodity.id) == (str(m)[1:2]):
                    commodity_name.append(commodity.commodity_Name)
                    commodity_price.append(commodity.commodity_price)
            context = {'nlist' : commodity_name, 'plist' : commodity_price, 't' : t}
            if True:
                return render(request,'shopping.html',context)
            else:
                return HttpResponseRedirect('login_success.html')

def video_sopping(request):
    return StreamingHttpResponse(gen2(VideoCamera2()),content_type=\
        'multipart/x-mixed-replace; boundary=frame')

def gen2(camera):
    while True:
        frame= camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# 購物車
class shopping_cart(View):
    def get(self,request):
        global t
        sum = 0
        for price in commodity_price:
            sum += int(price)
        context = {'nlist' : commodity_name, 'plist' : commodity_price , 't':t , 'sum' : sum}     
        return render(request , "shopping_cart.html" , context)
    def post(self , request):
        global t
        if logout in request.POST:
            t = ""
            context = {'commoditylist' : commoditylist , 't' : t}
            return render(request , "index.html" , context)

# 結帳
class checkout(View):  
    def get(self , request):
        global t
        sum = 0
        for price in commodity_price:
            sum += int(price)
        context = {'nlist' : commodity_name, 'plist' : commodity_price , 't':t , 'sum' : sum}     
        return render(request , "checkout.html" , context) 
    def post(self , request):
        global t
        if logout in request.POST:
            t = ""
            context = {'commoditylist' : commoditylist , 't' : t}
            return render(request , "index.html" , context)

class show(View):
    def get(self , request):
        global t
        member_get = member.objects.get(cName = t)
        context = {'t' : t ,'memberlist_get' : member_get}
        return render(request,'show.html',context)
    def post(self,request):
        global t
        if logout in request.POST:
            t = ""
            context = {'commoditylist' : commoditylist , 't' : t}
            return render(request , "index.html" , context)

# 修改個人資料
class revise(View):
    def get(self , request):
        global t
        member_get = member.objects.get(cName = t)
        context = {'t' : t , 'memberlist_get' : member_get}
        return render(request , "revise.html" , context)
    def post(self,request): 
        global t
        if logout in request.POST:
            t = ""
            context = {'commoditylist' : commoditylist , 't' : t}
            return render(request , "index.html" , context)
        else:
            member_get = member.objects.get(cName = t)
            allowedname=['jpg','png']  
            member_get.cName = request.POST['name']
            member_get.cSex = request.POST['sex']
            member_get.cEmail = request.POST['email']
            member_get.cPassward = request.POST['passward']
            if len(request.POST['photo1'])>0:
                member_get.cPhoto1 = request.POST['photo1']
                extenedname1= member_get.cPhoto1.name[member_get.cPhoto1.name.rindex('.')+1:]
                if extenedname1 not in  allowedname:
                    return Http404()
            if len(request.POST['photo2'])>0:
                member_get.cPhoto2 = request.POST['photo2']
                extenedname2=member_get.cPhoto2.name[member_get.cPhoto2.name.rindex('.')+1:]
                if extenedname2 not in allowedname:
                    return Http404()
            if len(request.POST['photo3']) > 0:
                member_get.cPhoto3 = request.POST['photo3']
                extenedname3=member_get.cPhoto3.name[member_get.cPhoto3.name.rindex('.')+1:]
                if extenedname3 not in allowedname:
                    return Http404()            
            member_get.save()
            member_revise = member.objects.get(cName = member_get.cName)
            context = {"memberlist_get":member_revise , 't' :t}
            return render(request , "show.html" ,context )   
# Create your views here. 
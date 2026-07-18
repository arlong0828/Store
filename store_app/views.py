"""Web views for the store experience.

AI and camera dependencies are imported only when their endpoints are used, so
the catalogue and account pages can still run in a lightweight web environment.
"""

from pathlib import Path

from django.http import Http404, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views import View

from store.settings import BASE_DIR

from .models import commodity, faceID, member


def catalogue():
    return commodity.objects.all()


def member_name(request):
    return request.session.get("member_name", "")


def cart_context(request):
    items = request.session.get("cart_items", [])
    total = sum(int(item.get("price", 0)) for item in items)
    return {"cart_items": items, "total": total, "t": member_name(request)}


def handle_logout(request):
    if request.method == "POST" and "logout" in request.POST:
        request.session.flush()
        return redirect("home")
    return None


def require_member(request):
    if not member_name(request):
        return redirect("login")
    return None


class HomeView(View):
    def get(self, request):
        return render(request, "pages/home.html", {"commoditylist": catalogue()})


class RegisterView(View):
    allowed_extensions = {".jpg", ".jpeg", ".png"}

    def get(self, request):
        return render(request, "pages/register.html")

    def post(self, request):
        photos = [request.FILES.get(f"cPhoto{number}") for number in range(1, 4)]
        if any(photo is None for photo in photos):
            return render(request, "pages/register.html", {"t": "請上傳三張辨識照片。"}, status=400)
        if any(Path(photo.name).suffix.lower() not in self.allowed_extensions for photo in photos):
            raise Http404("只接受 JPG 或 PNG 圖片。")

        name = request.POST.get("cName", "").strip()
        face_image = faceID.objects.create(faceID_name=name)
        account = member.objects.create(
            cName=name,
            cSex=request.POST.get("cSex", ""),
            cEmail=request.POST.get("cEmail", "").strip(),
            cPassward=request.POST.get("cPassward", ""),
            cPhoto1=photos[0],
            cPhoto2=photos[1],
            cPhoto3=photos[2],
        )

        try:
            from .services.face_training import train_member_face

            train_member_face(account)
        except Exception:
            account.delete()
            face_image.delete()
            return render(
                request,
                "pages/register.html",
                {"t": "辨識服務目前無法完成註冊，請稍後再試。"},
                status=503,
            )

        request.session["member_name"] = account.cName
        return redirect("home-authenticated")


class LoginView(View):
    def get(self, request):
        return render(request, "pages/login.html")

    def post(self, request):
        try:
            from azure.cognitiveservices.vision.face import FaceClient
            from msrest.authentication import CognitiveServicesCredentials

            from .services.azure_config import azure_face_credentials
            from .services.image_upload import upload_image

            image_url = upload_image(BASE_DIR / "static/camera/tem.jpg")
            key, endpoint = azure_face_credentials()
            client = FaceClient(endpoint, CognitiveServicesCredentials(key))
            detected = client.face.detect_with_url(url=image_url)
            face_ids = [face.face_id for face in detected]
            results = client.face.identify(face_ids, "school_face_identification")

            matched_name = ""
            people = {str(person.faceID_number): person.faceID_name for person in faceID.objects.all()}
            for result in results:
                if result.candidates:
                    matched_name = people.get(str(result.candidates[0].person_id), "")
                    if matched_name:
                        break
        except Exception:
            matched_name = ""

        if not matched_name:
            return render(
                request,
                "pages/register.html",
                {"t": "登入失敗，尚未找到相符會員，請重新嘗試或建立帳號。"},
                status=401,
            )

        request.session["member_name"] = matched_name
        request.session.setdefault("cart_items", [])
        return redirect("home-authenticated")


def stream(camera):
    while True:
        frame = camera.get_frame()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"


def video_face(request):
    from .services.camera import VideoCamera

    return StreamingHttpResponse(stream(VideoCamera()), content_type="multipart/x-mixed-replace; boundary=frame")


def video_shopping(request):
    from .services.camera import ProductCamera

    return StreamingHttpResponse(stream(ProductCamera()), content_type="multipart/x-mixed-replace; boundary=frame")


class MemberHomeView(View):
    def get(self, request):
        blocked = require_member(request)
        if blocked:
            return blocked
        return render(request, "pages/member_home.html", {"commoditylist": catalogue(), "t": member_name(request)})

    def post(self, request):
        return handle_logout(request) or self.get(request)


class ShoppingView(View):
    def get(self, request):
        blocked = require_member(request)
        return blocked or render(request, "pages/shopping.html", cart_context(request))

    def post(self, request):
        logout_response = handle_logout(request)
        if logout_response:
            return logout_response
        blocked = require_member(request)
        if blocked:
            return blocked

        try:
            import cv2
            import numpy as np
            from tensorflow.keras.models import load_model

            image = cv2.imread(str(BASE_DIR / "static/camera/tem.jpg"))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, dsize=(100, 100))
            feature = np.array([resized]).reshape(1, 100, 100, 1).astype("float32") / 255
            model = load_model(BASE_DIR / "static/model/shoes_CNN_Model_0.84.h5")
            prediction = int(np.argmax(model.predict(feature), axis=-1)[0])
            product = commodity.objects.get(id=prediction)
        except Exception:
            return render(request, "pages/shopping.html", cart_context(request), status=422)

        items = request.session.get("cart_items", [])
        items.append({"name": product.commodity_Name, "price": product.commodity_price})
        request.session["cart_items"] = items
        request.session.modified = True
        return redirect("shopping")


class ShoppingCartView(View):
    def get(self, request):
        blocked = require_member(request)
        return blocked or render(request, "pages/cart.html", cart_context(request))

    def post(self, request):
        return handle_logout(request) or self.get(request)


class CheckoutView(View):
    def get(self, request):
        blocked = require_member(request)
        return blocked or render(request, "pages/checkout.html", cart_context(request))

    def post(self, request):
        logout_response = handle_logout(request)
        if logout_response:
            return logout_response
        blocked = require_member(request)
        if blocked:
            return blocked
        request.session["cart_items"] = []
        return redirect("home-authenticated")


class ProfileView(View):
    def get(self, request):
        blocked = require_member(request)
        if blocked:
            return blocked
        account = member.objects.filter(cName=member_name(request)).first()
        if not account:
            request.session.flush()
            return redirect("login")
        return render(request, "pages/profile.html", {"t": account.cName, "memberlist_get": account})

    def post(self, request):
        return handle_logout(request) or self.get(request)


class ProfileEditView(View):
    allowed_extensions = RegisterView.allowed_extensions

    def get(self, request):
        blocked = require_member(request)
        if blocked:
            return blocked
        account = member.objects.filter(cName=member_name(request)).first()
        return render(request, "pages/profile_edit.html", {"t": member_name(request), "memberlist_get": account})

    def post(self, request):
        logout_response = handle_logout(request)
        if logout_response:
            return logout_response
        blocked = require_member(request)
        if blocked:
            return blocked

        account = member.objects.get(cName=member_name(request))
        account.cName = request.POST.get("name", account.cName).strip()
        account.cSex = request.POST.get("sex", account.cSex)
        account.cEmail = request.POST.get("email", account.cEmail).strip()
        account.cPassward = request.POST.get("passward", account.cPassward)
        for number in range(1, 4):
            photo = request.FILES.get(f"photo{number}")
            if photo:
                if Path(photo.name).suffix.lower() not in self.allowed_extensions:
                    raise Http404("只接受 JPG 或 PNG 圖片。")
                setattr(account, f"cPhoto{number}", photo)
        account.save()
        request.session["member_name"] = account.cName
        return redirect("profile")

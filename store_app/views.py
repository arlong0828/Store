"""Web views for the store experience.

AI and camera dependencies are imported only when their endpoints are used, so
the catalogue and account pages can still run in a lightweight web environment.
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

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
            from .services.local_face import FaceRecognitionError, enroll_member

            enroll_member(account)
        except (FaceRecognitionError, OSError, ValueError) as error:
            account.delete()
            faceID.objects.filter(faceID_name=name).delete()
            return render(
                request,
                "pages/register.html",
                {"error": f"無法建立本機人臉特徵：{error}"},
                status=422,
            )

        request.session["member_name"] = account.cName
        return redirect("home-authenticated")


class LoginView(View):
    max_image_size = 5 * 1024 * 1024
    allowed_content_types = {"image/jpeg", "image/png", "image/webp"}

    def get(self, request):
        return render(request, "pages/login.html")

    def post(self, request):
        image = request.FILES.get("face_image")
        if image is None:
            return render(
                request,
                "pages/login.html",
                {"error": "尚未取得鏡頭影像，請允許相機權限後再試一次。"},
                status=400,
            )
        if image.size > self.max_image_size or image.content_type not in self.allowed_content_types:
            return render(
                request,
                "pages/login.html",
                {"error": "鏡頭影像格式不正確或超過 5 MB。"},
                status=400,
            )

        try:
            from .services.local_face import FaceRecognitionError, recognize_member

            suffix = Path(image.name).suffix or ".jpg"
            with NamedTemporaryFile(suffix=suffix) as captured:
                for chunk in image.chunks():
                    captured.write(chunk)
                captured.flush()
                matched_name, _score = recognize_member(captured.name)
        except (FaceRecognitionError, OSError, ValueError) as error:
            return render(
                request,
                "pages/login.html",
                {"error": f"本機辨識失敗：{error}"},
                status=422,
            )

        if not matched_name:
            return render(
                request,
                "pages/login.html",
                {"error": "沒有找到相符會員，請調整角度後重試，或先建立帳號。"},
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
        old_name = account.cName
        photos_changed = False
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
                photos_changed = True
        account.save()

        profile = faceID.objects.filter(faceID_name=old_name).first()
        if profile and old_name != account.cName:
            profile.faceID_name = account.cName
            profile.save(update_fields=["faceID_name"])

        if photos_changed:
            try:
                from .services.local_face import enroll_member

                enroll_member(account)
            except Exception as error:
                return render(
                    request,
                    "pages/profile_edit.html",
                    {"t": account.cName, "memberlist_get": account, "error": f"照片已儲存，但人臉特徵更新失敗：{error}"},
                    status=422,
                )
        request.session["member_name"] = account.cName
        return redirect("profile")

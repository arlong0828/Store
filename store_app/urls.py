from django.urls import path

from . import views


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("streams/face/", views.video_face, name="video-face"),
    path("streams/product/", views.video_shopping, name="video-shopping"),
    path("index/", views.MemberHomeView.as_view(), name="home-authenticated"),
    path("shopping/", views.ShoppingView.as_view(), name="shopping"),
    path("shopping-cart/", views.ShoppingCartView.as_view(), name="shopping-cart"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile-edit"),
]

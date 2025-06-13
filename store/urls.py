"""store URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from store_app.views import index,login,register,shopping,checkout,shopping_cart,show,\
video_face,video_sopping,login_success_index,revise
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index.as_view()),
    path("register/" , register.as_view()),
    path("login/", login.as_view()),
    path("face/",video_face,name = "video_face"),
    path("shopping/",shopping.as_view()),
    path("sopping/" , video_sopping , name= "video_shopping"),
    path("checkout/",checkout.as_view()),
    path("shopping_cart/",shopping_cart.as_view()),
    path('show/',show.as_view()),
    path('index/',login_success_index.as_view()),
    path('revise/',revise.as_view()),
]

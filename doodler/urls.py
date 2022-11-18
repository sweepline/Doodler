"""doodler URL Configuration

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
from django.urls import path

from doodler.views import HomeView, AnswerView, OwnerView, ThanksView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("<uuid:doodle>", AnswerView.as_view(), name="answer"),
    path("owner/<uuid:doodle>", OwnerView.as_view(), name="owner"),
    path("thanks/<uuid:doodle>", ThanksView.as_view(), name="thanks"),
]

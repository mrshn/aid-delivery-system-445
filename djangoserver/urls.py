from django.contrib import admin
from django.urls import path
from forms_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('submit/', views.submit_form, name='submit_form'),
]
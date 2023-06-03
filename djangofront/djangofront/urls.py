"""djangofront URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path
from aid_delivery import views as adviews

urlpatterns = [
    re_path(r'^$', adviews.index, name='Home'),
    re_path(r'^add_request$', adviews.add_request, name='Request'),
    re_path(r'^update_request$', adviews.update_request, name='Request'),
    re_path(r'^delete_request$', adviews.delete_request, name='Request'),
    re_path(r'^mark_available_request$', adviews.mark_available_request, name='Request'),
    re_path(r'^pick_request$', adviews.pick_request, name='Request'),
    re_path(r'^arrived_request$', adviews.arrived_request, name='Request'),
    re_path(r'^new_instance$', adviews.new_campaign, name='Campaign'),
    re_path(r'^open_instance$', adviews.open_campaign, name='Campaign'),
    re_path(r'^list_instances$', adviews.list_campaign, name='Campaign'),
    re_path(r'^close_instance$', adviews.close_campaign, name='Campaign'),
    re_path(r'^add_catalog_item$', adviews.add_catalog_item, name='Catalog'),
    re_path(r'^update_catalog_item$', adviews.update_catalog_item, name='Catalog'),
    re_path(r'^search_catalog_item$', adviews.search_catalog_item, name='Catalog'),
    re_path(r'^logout$', adviews.logout_get, name='Logout'),
    re_path(r'^loginp$', adviews.login_post, name='Login'),
    re_path(r'^login$', adviews.login_view, name='Login'),
    re_path(r'^registerp$', adviews.register_post, name='Register'),
    re_path(r'^register$', adviews.register_view, name='Register'),
    path('admin/', admin.site.urls),
]

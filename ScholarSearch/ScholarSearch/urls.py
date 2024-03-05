"""
URL configuration for ScholarSearch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from . import views
# from .views import home, paper_detail


urlpatterns = [
    path('', views.home, name='home'),
    path('paper/<str:object_id>/', views.paper_detail, name='paper_detail'),
    path('search/', views.run_search, name='run_search'),
    path('search', views.search, name='search'),
    path('results/', views.search_results, name='search_results'),
    path('admin/', admin.site.urls),
]

"""sf_t3d URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
#from sf_user import views as user_views
from authosm import views as user_views
from sf_t3d import views

app_name = 'base'
urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^auth/$', user_views.user_login, name='auth_user'),
    #url(r'^register', user_views.register_view, name='register_user'),
    url(r'^projects/', include('projecthandler.urls.project', namespace='projects'), name='projects_base'),

    url(r'^$', views.home, name='home'),
    url(r'^home', views.home, name='home'),
    url(r'^forbidden', views.forbidden, name='forbidden'),

]

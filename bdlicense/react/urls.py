from django.conf.urls import patterns, url
from . import views
urlpatterns = patterns(
    '',
    url(r'^adminuserlogin',views.Login, name='register'),
)
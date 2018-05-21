from . import views

from django.conf.urls import url, include

urlpatterns = [
    url(r'^guest/([A-Za-z0-9]{6})/([A-Za-z0-9]{6})/?', views.guest_login),
    url(r'^guest/?$', views.guest_details, name='guest-details'),
    url(r'^details/?$', views.content_page, {"page_name": "detail"}, name='details'),
    url(r'^photos/?', views.photos, name='photos'),
    url(r'^gifts/?', views.content_page, {"page_name": "gifts"}, name='gifts'),
    url(r'^story/?', views.content_page, {"page_name": "story"}, name='story'),
    url(r'^404', views.content_page, {"page_name": "error404"}),
    url(r'^staff/mailout/([0-9]+)', views.mailout, name='mailout'),
    url(r'^$', views.index, name='home'),
]

from . import admin, views, path_converters, staff_urls
from django.urls import path, register_converter, include

register_converter(path_converters.PnrConverter, 'pnr')

urlpatterns = [
    path('guest/<pnr:pnr>/<pnr:open_key>', views.guest_login),
    path('guest', views.guest_details, name='guest-details'),
    path('details', views.content_page, {"page_name": "detail"}, name='details'),
    path('photos', views.photos, name='photos'),
    path('gifts', views.content_page, {"page_name": "gifts"}, name='gifts'),
    path('story', views.content_page, {"page_name": "story"}, name='story'),
    path('404', views.content_page, {"page_name": "error404"}),
    path('staff/', include(staff_urls.urlpatterns)),
    path('admin/', admin.site.urls),
    path('', views.index, name='home')
]

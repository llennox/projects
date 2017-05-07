
from django.conf.urls import url, include 
from django.contrib import admin
from gpp import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.DefaultRouter()
#makes sure that the API endpoints work
router.register(r'api/User', views.UserViewSet)
router.register(r'api/Group', views.GroupViewSet)
admin.autodiscover()



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home_page, name='home_page'),
    url(r'^sign_page/$', views.sign_page, name='sign_page'),
    url(r'^upload/$', views.upload_page, name='upload_page'),
    url(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z)$', views.photo_page, name='photo_page'),
    url(r'^viewProfile_page/(?P<username>.+)/$', views.viewProfile_page, name='viewProfile_page'),
    url(r'^editProfileImg/(?P<username>.+)/$', views.editProfileImg, name='editProfile_page'),
    url(r'^editBio/(?P<username>.+)/$', views.editBio, name='editProfile_page'),
    url(r'^photos/$', views.photos_page, name='photos_page'),
    url(r'^photoView/(?P<uuid>.+)/$', views.photo_page, name='photoView'),
    url(r'^messages/$', views.messages_page, name='messages_page'),
    url(r'^logout_page/$', views.logout_view, name='logout_view'),
    url(r'^register_page/$', views.register_page, name='register_page'),
    url(r'^activate/(?P<key>.+)$', views.activation, name='activation'),
    url(r'^new-activation-link/(?P<user_id>.+)/$',views.new_activation_link, name='new_activation_link'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^reset_password/$', views.reset_password, name='reset_password'),
    url(r'^delete_photo/(?P<uuid>.+)/(?P<username>.+)/$', views.delete_photo, name='delete_photo'),
    url(r'^flag_photo/(?P<uuid>.+)/$', views.flag_photo, name='flag_photo'),
    url(r'^delete_comment/(?P<uuid>.+)/(?P<username>.+)/(?P<photouuid>.+)/$', views.delete_comment, name='delete_comment'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/photos/$', views.PhotoViewSet.as_view()),
    url(r'^api/comments/$', views.CommentViewSet.as_view()),
    url(r'^api/photos/(\-?\d{1,2}\.\d{3,10})/(\-?\d{1,2}\.\d{3,10})/$', views.PhotoViewSet.as_view()),
    url(r'^api_documentation/$', views.api_documentation, name='api_documentation'),



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#urlpatterns = format_suffix_patterns(urlpatterns)







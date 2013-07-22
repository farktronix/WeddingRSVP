from django.conf.urls.defaults import *

urlpatterns = patterns('reply.views',
    (r'^$', 'index'),
    (r'^new/$', 'newreply'),
    (r'^update/$', 'updatereply'),
)
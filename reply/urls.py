from django.conf.urls.defaults import *

urlpatterns = patterns('reply.views',
    (r'^$', 'index'),
    (r'^(?P<reply_id>\d+)/$', 'detail'),
    (r'^new/$', 'newreply'),
    (r'^(?P<reply_id>\d+)/update/$', 'updatereply'),
)
from django.conf.urls.defaults import *

urlpatterns = patterns('summary.views',
    (r'^$', 'index'),
    (r'^new/$', 'newreply'),
    (r'^(?P<reply_uuid>.*)/update/$', 'updatereply'),
)
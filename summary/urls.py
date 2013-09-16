from django.conf.urls.defaults import *

urlpatterns = patterns('summary.views',
    (r'^$', 'index'),
    (r'^new/$', 'newreply'),
    (r'^emails/$', 'emails'),
    (r'^updateemails/$', 'updateemails'),
    (r'^createupdate/$', 'createupdate'),
    (r'^listpeople/$', 'listpeople'),
    (r'^updateperson/$', 'updateperson'),
    (r'^noreply/$', 'noreply'),
)
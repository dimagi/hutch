from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
                       (r'^hutch/imgproxy/(?P<doc_id>[0-9a-fA-Z]{25,32})/(?P<attachment_key>.*)$', 'hutch.views.image_proxy'),
                       )

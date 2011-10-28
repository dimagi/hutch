from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
                       url(r'^hutch/imgproxy/(?P<doc_id>[0-9a-fA-Z]{25,32})/(?P<attachment_key>.*)$', 'hutch.views.image_proxy', name='hutch_proxy_original'),
                       url(r'^hutch/image/(?P<attachment_image_id>[0-9a-fA-Z]{25,32})/$', 'hutch.views.show_image', name='hutch_show_image'),
                       )

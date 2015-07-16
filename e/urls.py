# -*- coding: utf-8 -*-
from django.conf.urls import include, url, patterns
from django.contrib import admin
from item.views import *
# from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings as st
import os

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
	url(r'^preparevps/$', preparevps),
	url(r'^install_socks/$', install_socks),
	url(r'^create_file_ams/$', create_file_ams),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(st.BASE_DIR, 'media')}),
	url(r'^admin/', include(admin.site.urls)),    
    url(r'^$', index),
    
]


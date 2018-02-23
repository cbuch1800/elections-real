"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, handler404, handler500
from django.contrib import admin
from django.contrib.auth import views as auth_views
from elections.views import error_404, error_500

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name':'registration/logout.html'}, name='logout'),
    url(r'^password/reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^', include('elections.urls', namespace='elections')),
]

handler404 = error_404
handler500 = error_500
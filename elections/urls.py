from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # url(r'^login/$', auth_views.login, name='login'),
    # url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^$', welcome, name='home'),
    # url(r'^feed/$', newsfeed, name='newsfeed'),
    # url(r'^feed/new/$', new_post, name='new_post'),
    # url(r'^feed/image/$', new_image, name='new_image'),
    # url(r'^profiles/$', view_candidates, name='profiles'),
    # url(r'^profiles/edit/$', edit_profiles, name='edit_profiles'),
    # url(r'^profiles/edit/(\d+)/$', edit_candidate, name='edit_candidate'),
    # url(r'^u/(\d+)/$', candidate_profile, name='candidate_profile'),
    url(r'^register/$', add_candidate, name='candidate_reg'),
    url(r'^elections/$', open_elections, name='elections'),
    url(r'^elections/(\d+)/$', ballot, name='ballot'),
    url(r'^results/$', view_results, name='results'),
    url(r'^tools/$', admin_tools, name='tools'),
    url(r'^tools/result/(\d+)/$', get_results, name='get_results'),
    url(r'^password/new/$', password_change, name='change_password'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^signup/sent/$', account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:

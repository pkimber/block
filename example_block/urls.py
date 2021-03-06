# -*- encoding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from block.models import Page
from block.views import (
    PageDesignView,
    PageTemplateView,
)

from .views import (
    ExampleView,
    SettingsView,
    TitleCreateView,
    TitlePublishView,
    TitleRemoveView,
    TitleUpdateView,
)


admin.autodiscover()


urlpatterns = [
    # '/' send to home
    url(regex=r'^$',
        view=PageTemplateView.as_view(),
        kwargs=dict(page=Page.HOME),
        name='project.home'
        ),
    # admin, login
    url(regex=r'^admin/',
        view=include(admin.site.urls)
        ),
    url(regex=r'^block/',
        view=include('block.urls.block')
        ),
    url(regex=r'^settings/$',
        view=SettingsView.as_view(),
        name='project.settings'
        ),
    url(regex=r'^wizard/',
        view=include('block.urls.wizard')
        ),
    url(regex=r'^',
        view=include('login.urls')
        ),
    # home page when logged in
    url(r'^home/user/$',
        view=RedirectView.as_view(url=reverse_lazy('project.home'), permanent=False),
        name='project.dash'
        ),
    # custom page - see https://www.pkimber.net/open/app-block.html
    url(regex=r'^calendar/information/$',
        view=ExampleView.as_view(),
        kwargs=dict(page=Page.CUSTOM, menu='calendar-information'),
        name='calendar.information'
        ),
    # block page design
    url(regex=r'^(?P<page>[-\w\d]+)/design/$',
        view=PageDesignView.as_view(),
        name='project.page.design'
        ),
    url(regex=r'^(?P<page>[-\w\d]+)/(?P<menu>[-\w\d]+)/design/$',
        view=PageDesignView.as_view(),
        name='project.page.design'
        ),
    # block page view
    url(regex=r'^(?P<page>[-\w\d]+)/$',
        view=PageTemplateView.as_view(),
        name='project.page'
        ),
    url(regex=r'^(?P<page>[-\w\d]+)/(?P<menu>[-\w\d]+)/$',
        view=PageTemplateView.as_view(),
        name='project.page'
        ),
    # title create, publish, update and remove
    url(regex=r'^title/create/(?P<page>[-\w\d]+)/(?P<section>[-\w\d]+)/$',
        view=TitleCreateView.as_view(),
        name='example.title.create'
        ),
    url(regex=r'^title/create/(?P<page>[-\w\d]+)/(?P<menu>[-\w\d]+)/(?P<section>[-\w\d]+)/$',
        view=TitleCreateView.as_view(),
        name='example.title.create'
        ),
    url(regex=r'^title/(?P<pk>\d+)/publish/$',
        view=TitlePublishView.as_view(),
        name='example.title.publish'
        ),
    url(regex=r'^title/(?P<pk>\d+)/update/$',
        view=TitleUpdateView.as_view(),
        name='example.title.update'
        ),
    url(regex=r'^title/(?P<pk>\d+)/remove/$',
        view=TitleRemoveView.as_view(),
        name='example.title.remove'
        ),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#   ^ helper function to return a URL pattern for serving files in debug mode.
# https://docs.djangoproject.com/en/1.5/howto/static-files/#serving-files-uploaded-by-a-user

if settings.ALLOW_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
